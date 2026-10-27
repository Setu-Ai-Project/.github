import type { SubmissionResult } from "@/types/submission";
import { mockSubmit } from "./mockSubmission";

// The backend isn't ready yet, so we use the mock. When it's ready, this becomes
// false and NEXT_PUBLIC_API_URL gets set. Nothing else in the app has to change.
export const USE_MOCK = true;

export async function submitAnswer(
  challengeId: string,
  answer: string
): Promise<SubmissionResult> {
  if (USE_MOCK) return mockSubmit(answer);

  // Real backend (not used yet).
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ challengeId, answer }),
  });
  if (!res.ok) throw new Error("Submission request failed");
  return res.json();
}