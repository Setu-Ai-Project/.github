import type { SubmissionResult } from "@/types/submission";
import { mockSubmit } from "./mockSubmission";

// Falls back to mock if NEXT_PUBLIC_API_URL is unset.
export const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export async function submitAnswer(
  challengeId: string,
  answer: string,
  token?: string
): Promise<SubmissionResult> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (USE_MOCK || !apiUrl) {
    return mockSubmit(answer);
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${apiUrl}/submissions`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      challenge_id: Number(challengeId),
      answer_text: answer,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || "Submission request failed");
  }

  const data = await res.json();
  return {
    status: data.status,
    feedback: data.feedback || [],
    xpEarned: data.xp_awarded ?? 0,
  };
}