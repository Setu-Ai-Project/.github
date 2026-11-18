"use client";

import { useCallback } from "react";

import { getQuiz } from "@/api/learningApi";
import ErrorState from "@/app/components/common/ErrorState";
import LoadingState from "@/app/components/common/LoadingState";
import ScreenShell from "@/app/components/common/ScreenShell";
import { useAsync } from "@/hooks/useAsync";
import QuizPlayer from "./QuizPlayer";

type QuizScreenProps = {
  moduleId: string;
};

// Loads the quiz for a module, then hands it to QuizPlayer.
export default function QuizScreen({ moduleId }: QuizScreenProps) {
  // useCallback keeps the load function stable, so useAsync loads only once.
  const loadQuiz = useCallback(() => getQuiz(moduleId), [moduleId]);
  const { data, loading, error, reload } = useAsync(loadQuiz);

  function renderBody() {
    if (loading) return <LoadingState message="Getting your quiz ready..." />;
    if (error || !data) return <ErrorState onRetry={reload} />;

    if (data.questions.length === 0) {
      return (
        <div className="flex flex-col gap-4">
          <h1 className="break-words font-display text-3xl font-bold">{data.title}</h1>
          <p>This quiz has no questions yet. Check back soon!</p>
        </div>
      );
    }

    // The key starts a fresh game if a different quiz is ever loaded.
    return <QuizPlayer key={data.id} quiz={data} moduleId={moduleId} />;
  }

  return (
    <ScreenShell label="Quiz" backHref={`/learn/${moduleId}`} backLabel="Back to lesson">
      {renderBody()}
    </ScreenShell>
  );
}
