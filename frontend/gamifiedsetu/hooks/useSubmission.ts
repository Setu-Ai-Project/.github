"use client";

import { useRef, useState } from "react";
import { submitAnswer } from "@/api/submissionApi";
import type { SubmissionResult, UiState } from "@/types/submission";

export function useSubmission(challengeId: string) {
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [uiState, setUiState] = useState<UiState>("idle");
  const [totalXp, setTotalXp] = useState(0);
  const inFlight = useRef(false);

  async function submit(answer: string) {
    if (inFlight.current) return;
    inFlight.current = true;

    setUiState("submitting");
    setResult({ status: "pending", feedback: [], xpEarned: 0 });

    try {
      const response = await submitAnswer(challengeId, answer);
      setResult(response);
      setUiState("done");
      if (response.status === "passed") {
        setTotalXp((prev) => prev + response.xpEarned);
      }
    } catch {
      setResult(null);
      setUiState("error");
    } finally {
      inFlight.current = false;
    }
  }

  function retry() {
    setResult(null);
    setUiState("idle");
  }

  return { result, uiState, totalXp, submit, retry };
}