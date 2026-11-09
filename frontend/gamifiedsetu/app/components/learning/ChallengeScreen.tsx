
"use client";

import { useCallback, useState } from "react";
import Link from "next/link";

import { getBuilderChallenge } from "@/api/learningApi";
import { useAsync } from "@/hooks/useAsync";

import ScreenShell from "@/app/components/common/ScreenShell";
import LoadingState from "@/app/components/common/LoadingState";
import ErrorState from "@/app/components/common/ErrorState";

import ByteStrip from "@/app/components/mascots/ByteStrip";
import BugTooltip from "@/app/components/mascots/BugTooltip";
import SubmissionPanel from "@/app/components/submission/SubmissionPanel";

import HintList from "./HintList";

type ChallengeScreenProps = {
  moduleId: string;
};

export default function ChallengeScreen({
  moduleId,
}: ChallengeScreenProps) {
  const loadChallenge = useCallback(
    () => getBuilderChallenge(moduleId),
    [moduleId]
  );

  const { data, loading, error, reload } = useAsync(loadChallenge);

  const [showTip, setShowTip] = useState(true);
  const [revealedHints, setRevealedHints] = useState(0);
  const [showEncouragement, setShowEncouragement] = useState(false);

  if (loading) {
    return (
      <ScreenShell
        label="Builder Challenge"
        backHref={`/quiz/${moduleId}`}
        backLabel="Back to quiz"
      >
        <LoadingState message="Getting your challenge ready..." />
      </ScreenShell>
    );
  }

  if (error || !data) {
    return (
      <ScreenShell
        label="Builder Challenge"
        backHref={`/quiz/${moduleId}`}
        backLabel="Back to quiz"
      >
        <ErrorState
          message={error?.message ?? "Could not load this challenge."}
          onRetry={reload}
        />
      </ScreenShell>
    );
  }

  return (
    <ScreenShell
      label="Builder Challenge"
      backHref={`/quiz/${moduleId}`}
      backLabel="Back to quiz"
    >
      <div className="space-y-6">
        {showTip && (
          <ByteStrip
            message="Tip: start small, test often."
            onDismiss={() => setShowTip(false)}
          />
        )}

        <h1 className="text-3xl font-bold">{data.title}</h1>

        <section>
          <h2 className="mb-2 text-xl font-bold">Your goal</h2>
          <p className="leading-relaxed">{data.goal}</p>
        </section>

        <section className="rounded-xl border border-ink/10 bg-white p-5">
          <h2 className="mb-3 text-xl font-bold">Instructions</h2>
          <p className="whitespace-pre-line leading-relaxed">
            {data.instructions}
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold">Hints</h2>

          <HintList
            hints={data.hints}
            onReveal={(shownCount) => {
              setRevealedHints(shownCount);
              setShowEncouragement(true);
            }}
          />

          {showEncouragement && (
            <div className="mt-4">
              <BugTooltip
                key={revealedHints}
                message="Here's a nudge. You've got this!"
                onDismiss={() => setShowEncouragement(false)}
              />
            </div>
          )}
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold">Your work</h2>
          <SubmissionPanel challengeId={data.id} />
        </section>

        <Link
          href={`/module/${moduleId}`}
          className="inline-block font-bold text-coral hover:underline"
        >
          Back to module
        </Link>
      </div>
    </ScreenShell>
  );
}
