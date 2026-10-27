import type { SubmissionResult } from "@/types/submission";

export const MOCK_DELAY_MS = 1200;

export async function mockSubmit(answer: string): Promise<SubmissionResult> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));

  if (answer.trim().toLowerCase() === "correct") {
    return { status: "passed", feedback: ["Great job!"], xpEarned: 50 };
  }

  return {
    status: "needs_revision",
    feedback: [
      "Your answer is missing the loop condition.",
      "Hint: check that your counter actually increases.",
    ],
    xpEarned: 0,
  };
}