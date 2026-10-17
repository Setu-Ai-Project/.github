"use client";

import { useState } from "react";
import { useSubmission } from "@/hooks/useSubmission";
import StatusBadge from "./StatusBadge";
import SubmitButton from "./SubmitButton";
import FeedbackList from "./FeedbackList";

type SubmissionPanelProps = {
  challengeId: string;
};

export default function SubmissionPanel({
  challengeId,
}: SubmissionPanelProps) {
  const [answer, setAnswer] = useState("");
  const { result, uiState, totalXp, submit, retry } =
    useSubmission(challengeId);

  const isChecking = uiState === "submitting";
  const isPassed = result?.status === "passed";
  const needsRevision = result?.status === "needs_revision";
  const answerId = `answer-${challengeId}`;

  return (
    <section className="w-full max-w-xl rounded-2xl border-4 border-ink bg-white p-4 shadow-[8px_8px_0_#172A32] sm:p-6">
      <label
        htmlFor={answerId}
        className="font-display text-lg font-bold text-ink"
      >
        Your answer
      </label>

      <textarea
        id={answerId}
        className="mt-2 h-32 w-full resize-y rounded-xl border-2 border-ink bg-cream p-3 text-ink placeholder:text-taskgray focus:outline-none focus:ring-2 focus:ring-coral disabled:opacity-60"
        placeholder="Type your answer here..."
        value={answer}
        onChange={(event) => setAnswer(event.target.value)}
        disabled={isChecking || isPassed}
      />

      {!isPassed && !needsRevision && (
        <div className="mt-4">
          <SubmitButton
            onClick={() => submit(answer)}
            loading={isChecking}
            disabled={answer.trim() === ""}
          />
        </div>
      )}

      <div aria-live="polite" className="mt-4 space-y-3">
        {result && <StatusBadge status={result.status} />}

        {needsRevision && result && (
          <>
            <FeedbackList items={result.feedback} />

            <button
              type="button"
              onClick={retry}
              className="rounded-2xl border-4 border-ink bg-white px-6 py-2 font-display text-lg font-bold text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5"
            >
              Try again
            </button>
          </>
        )}

        {isPassed && result && (
          <p className="font-display text-lg font-bold text-ink">
            You earned {result.xpEarned} XP! Total XP: {totalXp}
          </p>
        )}

        {uiState === "error" && (
          <p className="rounded-xl border-2 border-coral bg-cream p-3 font-bold text-ink">
            We could not check your answer. Please try again in a moment.
          </p>
        )}
      </div>
    </section>
  );
}