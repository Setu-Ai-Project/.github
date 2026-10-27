// Every status a submission can have. Using a union type means a typo like
// "passd" is a TypeScript error instead of a silent bug.
export type SubmissionStatus = "pending" | "passed" | "needs_revision";

// What one submission result looks like.
export interface SubmissionResult {
  status: SubmissionStatus;
  feedback: string[]; // specific tips shown to the learner
  xpEarned: number; // 0 when the answer did not pass
}

// Which "mood" the screen is in. This is only about our UI, not the server.
export type UiState = "idle" | "submitting" | "done" | "error";