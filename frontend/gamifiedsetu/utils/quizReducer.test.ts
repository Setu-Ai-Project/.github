import { describe, expect, it } from "vitest";

import type { AnswerCheck } from "@/types/learning";
import {
  initialQuizState,
  quizReducer,
  selectQuizMascot,
  type QuizState,
} from "./quizReducer";

const CORRECT: AnswerCheck = { correct: true, correctIndex: 1, explanation: "Yes!" };
const WRONG: AnswerCheck = { correct: false, correctIndex: 1, explanation: "No." };

// A state where option 0 is picked and checked with the given result.
function checkedWith(result: AnswerCheck): QuizState {
  const picked = quizReducer(initialQuizState, { type: "select", index: 0 });
  return quizReducer(picked, { type: "checkSuccess", result });
}

describe("quizReducer", () => {
  it("records the selected option", () => {
    const state = quizReducer(initialQuizState, { type: "select", index: 2 });
    expect(state.selectedIndex).toBe(2);
  });

  it("ignores a new selection once the answer is checked", () => {
    const state = quizReducer(checkedWith(WRONG), { type: "select", index: 3 });
    expect(state.selectedIndex).toBe(0);
  });

  it("ignores a new selection while checking", () => {
    const checking = quizReducer(initialQuizState, { type: "checkStart" });
    const state = quizReducer(checking, { type: "select", index: 1 });
    expect(state.selectedIndex).toBeNull();
  });

  it("adds a point for a correct answer only", () => {
    expect(checkedWith(CORRECT).score).toBe(1);
    expect(checkedWith(WRONG).score).toBe(0);
  });

  it("stops checking and stores the result on success", () => {
    const state = checkedWith(CORRECT);
    expect(state.checking).toBe(false);
    expect(state.checkResult).toEqual(CORRECT);
  });

  it("keeps the selection and flags the failure when a check fails", () => {
    const picked = quizReducer(initialQuizState, { type: "select", index: 2 });
    const checking = quizReducer(picked, { type: "checkStart" });
    const state = quizReducer(checking, { type: "checkFailure" });

    expect(state.checking).toBe(false);
    expect(state.checkFailed).toBe(true);
    expect(state.selectedIndex).toBe(2);
  });

  it("moves to the next question and clears the per-question state", () => {
    const state = quizReducer(checkedWith(CORRECT), { type: "next" });

    expect(state.currentIndex).toBe(1);
    expect(state.selectedIndex).toBeNull();
    expect(state.checkResult).toBeNull();
    expect(state.score).toBe(1);
  });

  it("does not move on before the answer is checked", () => {
    expect(quizReducer(initialQuizState, { type: "next" })).toBe(initialQuizState);
    expect(quizReducer(initialQuizState, { type: "finish" })).toBe(initialQuizState);
  });

  it("finishes the quiz after the last answer is checked", () => {
    expect(quizReducer(checkedWith(CORRECT), { type: "finish" }).finished).toBe(true);
  });

  it("restarts from the very beginning", () => {
    const finished = quizReducer(checkedWith(CORRECT), { type: "finish" });
    expect(quizReducer(finished, { type: "restart" })).toEqual(initialQuizState);
  });
});

describe("selectQuizMascot", () => {
  it("shows nothing before an answer is checked", () => {
    expect(selectQuizMascot(initialQuizState)).toBeNull();
  });

  it("matches the mascot to the result", () => {
    expect(selectQuizMascot(checkedWith(CORRECT))).toBe("correct");
    expect(selectQuizMascot(checkedWith(WRONG))).toBe("wrong");
  });

  it("shows the finish mascot on the results screen", () => {
    const finished = quizReducer(checkedWith(WRONG), { type: "finish" });
    expect(selectQuizMascot(finished)).toBe("finish");
  });

  it("hides the mascot once dismissed, until the next moment", () => {
    const dismissed = quizReducer(checkedWith(CORRECT), { type: "dismissMascot" });
    expect(selectQuizMascot(dismissed)).toBeNull();

    const finished = quizReducer(dismissed, { type: "finish" });
    expect(selectQuizMascot(finished)).toBe("finish");
  });
});
