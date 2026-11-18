"use client";

import { useReducer, useRef } from "react";

import { checkAnswer } from "@/api/learningApi";
import type { QuizQuestion } from "@/types/learning";
import {
  initialQuizState,
  quizReducer,
  selectQuizMascot,
} from "@/utils/quizReducer";

// Runs one quiz: which question is showing, checking answers, the score and the mascot.
// The rules themselves live in quizReducer; this hook adds the server call.
export function useQuiz(moduleId: string, questions: QuizQuestion[]) {
  const [state, dispatch] = useReducer(quizReducer, initialQuizState);

  // State updates don't land instantly, so a fast double-click could start two
  // checks. A ref updates immediately, so it stops the second one.
  const inFlight = useRef(false);

  const total = questions.length;
  const question = questions[state.currentIndex] ?? null;
  const isLast = state.currentIndex >= total - 1;

  // Asks the server whether the picked option is right. Never reads question.correctIndex.
  async function check() {
    if (inFlight.current) return;
    if (!question || state.selectedIndex === null || state.checkResult) return;
    inFlight.current = true;

    dispatch({ type: "checkStart" });
    try {
      const result = await checkAnswer(moduleId, question.id, state.selectedIndex);
      dispatch({ type: "checkSuccess", result });
    } catch {
      dispatch({ type: "checkFailure" });
    } finally {
      inFlight.current = false;
    }
  }

  // "Next question", or "See results" on the last one.
  function next() {
    dispatch({ type: isLast ? "finish" : "next" });
  }

  return {
    state,
    question,
    total,
    isLast,
    mascot: selectQuizMascot(state),
    select: (index: number) => dispatch({ type: "select", index }),
    check,
    next,
    dismissMascot: () => dispatch({ type: "dismissMascot" }),
    restart: () => dispatch({ type: "restart" }),
  };
}
