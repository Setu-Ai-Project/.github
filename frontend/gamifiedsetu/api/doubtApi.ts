import type { Doubt } from "@/types/doubt";
import {
  mockCreateDoubt,
  mockListDoubts,
  mockReplyToDoubt,
} from "./mockDoubtApi";

// When true, uses client-side localStorage simulation.
// When false, connects to the real backend via process.env.NEXT_PUBLIC_API_URL.
export const USE_MOCK = true;

export async function listDoubts(): Promise<Doubt[]> {
  if (USE_MOCK) {
    return mockListDoubts();
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/doubts`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Could not load doubts");
  }

  return res.json();
}

export async function createDoubt(
  question: string,
  learnerName: string
): Promise<Doubt> {
  if (USE_MOCK) {
    return mockCreateDoubt(question, learnerName);
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/doubts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, learnerName }),
  });

  if (!res.ok) {
    throw new Error("Could not send doubt");
  }

  return res.json();
}

export async function replyToDoubt(
  id: string,
  text: string,
  mentorName: string
): Promise<Doubt> {
  if (USE_MOCK) {
    return mockReplyToDoubt(id, text, mentorName);
  }

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/doubts/${id}/reply`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, mentorName }),
    }
  );

  if (!res.ok) {
    throw new Error("Could not send reply");
  }

  return res.json();
}
