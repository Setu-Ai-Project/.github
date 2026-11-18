import type { AnswerCheck } from "@/types/learning";

// Everything the quiz needs to remember while it is being played.
export type QuizState = {
  // Which question am I on? (0-based)
  currentIndex: number;
  // Which option has the learner picked? null = nothing yet.
  selectedIndex: number | null;
  // The server's verdict for this question. null = not checked yet.
  checkResult: AnswerCheck | null;
  // True while waiting for checkAnswer().
  checking: boolean;
  // True when the last check could not reach the server.
  checkFailed: boolean;
  // How many answers were correct so far.
  score: number;
  // True on the results screen.
  finished: boolean;
  // True once the learner closed the current mascot.
  mascotDismissed: boolean;
};

export type QuizAction =
  | { type: "select"; index: number }
  | { type: "checkStart" }
  | { type: "checkSuccess"; result: AnswerCheck }
  | { type: "checkFailure" }
  | { type: "next" }
  | { type: "finish" }
  | { type: "dismissMascot" }
  | { type: "restart" };

export type QuizMascotKind = "correct" | "wrong" | "finish";

export const initialQuizState: QuizState = {
  currentIndex: 0,
  selectedIndex: null,
  checkResult: null,
  checking: false,
  checkFailed: false,
  score: 0,
  finished: false,
  mascotDismissed: false,
};

// A pure function: given the current state and what just happened, return the new state.
// Every quiz rule lives here, so it can be tested without rendering anything.
export function quizReducer(state: QuizState, action: QuizAction): QuizState {
  switch (action.type) {
    case "select":
      // The answer is locked once it has been checked (or while checking).
      if (state.checkResult || state.checking || state.finished) return state;
      return { ...state, selectedIndex: action.index, checkFailed: false };

    case "checkStart":
      return { ...state, checking: true, checkFailed: false };

    case "checkSuccess":
      return {
        ...state,
        checking: false,
        checkResult: action.result,
        score: action.result.correct ? state.score + 1 : state.score,
        mascotDismissed: false,
      };

    case "checkFailure":
      // Keep the selection so the learner can simply press Check again.
      return { ...state, checking: false, checkFailed: true };

    case "next":
      if (!state.checkResult) return state;
      return {
        ...state,
        currentIndex: state.currentIndex + 1,
        selectedIndex: null,
        checkResult: null,
        checkFailed: false,
        mascotDismissed: false,
      };

    case "finish":
      if (!state.checkResult) return state;
      return { ...state, finished: true, mascotDismissed: false };

    case "dismissMascot":
      return { ...state, mascotDismissed: true };

    case "restart":
      return initialQuizState;
  }
}

// Which mascot to show right now. Derived from the state, so it can never disagree with it.
export function selectQuizMascot(state: QuizState): QuizMascotKind | null {
  if (state.mascotDismissed) return null;
  if (state.finished) return "finish";
  if (state.checkResult) return state.checkResult.correct ? "correct" : "wrong";
  return null;
}
