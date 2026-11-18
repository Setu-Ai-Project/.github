"use client";

import { useEffect, useRef } from "react";
import { MotionConfig, motion } from "motion/react";

import ProgressBar from "@/app/components/common/ProgressBar";
import { buttonClass } from "@/app/components/common/buttonStyles";
import { useQuiz } from "@/hooks/useQuiz";
import type { Quiz } from "@/types/learning";
import QuizMascot from "./QuizMascot";
import QuizQuestionCard from "./QuizQuestionCard";
import QuizResult from "./QuizResult";

type QuizPlayerProps = {
  quiz: Quiz;
  moduleId: string;
};

// Plays a loaded quiz: one question at a time, then the results.
// All the rules live in useQuiz; this component only draws them.
export default function QuizPlayer({ quiz, moduleId }: QuizPlayerProps) {
  const {
    state,
    question,
    total,
    isLast,
    mascot,
    select,
    check,
    next,
    dismissMascot,
    restart,
  } = useQuiz(moduleId, quiz.questions);

  // When the screen changes (next question, results, try again), the button the
  // learner pressed disappears or becomes disabled, which drops keyboard focus.
  // Move focus to the new content instead, so keyboard users never get lost.
  const questionLabelRef = useRef<HTMLParagraphElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Don't steal focus when the quiz first appears.
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (state.finished) titleRef.current?.focus();
    else questionLabelRef.current?.focus();
  }, [state.currentIndex, state.finished]);

  // A new key per moment makes each mascot appear fresh.
  const mascotNode = mascot && (
    <QuizMascot
      key={`${state.currentIndex}-${mascot}`}
      kind={mascot}
      score={state.score}
      total={total}
      onDismiss={dismissMascot}
    />
  );

  // tabIndex={-1}: can receive focus from code, but isn't an extra Tab stop.
  const title = (
    <h1
      ref={titleRef}
      tabIndex={-1}
      className="break-words font-display text-3xl font-bold focus:outline-none"
    >
      {quiz.title}
    </h1>
  );

  if (state.finished) {
    return (
      <div className="flex flex-col gap-6">
        {title}
        {mascotNode}
        <QuizResult score={state.score} total={total} moduleId={moduleId} onRetry={restart} />
      </div>
    );
  }

  if (!question) return null;

  const result = state.checkResult;
  const questionNumber = state.currentIndex + 1;

  return (
    <div className="flex flex-col gap-6">
      {title}

      <div className="flex flex-col gap-2">
        <p
          ref={questionLabelRef}
          tabIndex={-1}
          className="font-display text-sm font-bold focus:outline-none"
        >
          Question {questionNumber} of {total}
        </p>
        <ProgressBar value={questionNumber} max={total} label="Quiz progress" />
      </div>

      {/* A short fade-in for each new question. reducedMotion="user" skips it for
          learners who turned animations off in their device settings. */}
      <MotionConfig reducedMotion="user">
        <motion.div
          key={question.id}
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
        >
          <QuizQuestionCard
            question={question}
            selectedIndex={state.selectedIndex}
            onSelect={select}
            isChecked={result !== null}
            correctIndex={result?.correctIndex}
          />
        </motion.div>
      </MotionConfig>

      {/* aria-live lets screen readers announce the feedback as it appears. */}
      <div aria-live="polite" className="flex flex-col gap-2">
        {result && (
          <>
            <p className="font-display text-lg font-bold">
              {result.correct ? "Correct!" : "Not quite."}
            </p>
            {result.explanation && <p>{result.explanation}</p>}
          </>
        )}
        {state.checkFailed && (
          <p className="rounded-xl border-2 border-coral bg-cream p-3 font-bold">
            We could not check your answer. Please try again.
          </p>
        )}
      </div>

      {mascotNode}

      <div>
        {result ? (
          <button type="button" onClick={next} className={buttonClass("teal")}>
            {isLast ? "See results" : "Next question"}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => void check()}
            disabled={state.selectedIndex === null || state.checking}
            className={buttonClass("teal")}
          >
            {state.checking ? "Checking..." : "Check answer"}
          </button>
        )}
      </div>
    </div>
  );
}
