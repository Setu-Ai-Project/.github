
"use client";

import { useCallback, useState } from "react";
import Link from "next/link";

import { getLearnContent } from "@/api/learningApi";
import { useAsync } from "@/hooks/useAsync";
import ScreenShell from "@/app/components/common/ScreenShell";
import LoadingState from "@/app/components/common/LoadingState";
import ErrorState from "@/app/components/common/ErrorState";
import NovaBanner from "@/app/components/mascots/NovaBanner";
import LessonSection from "./LessonSection";

type LearnScreenProps = {
  moduleId: string;
};

export default function LearnScreen({ moduleId }: LearnScreenProps) {
  const loadLesson = useCallback(
    () => getLearnContent(moduleId),
    [moduleId]
  );

  const { data, loading, error, reload } = useAsync(loadLesson);

  const [currentSection, setCurrentSection] = useState(0);
  const [showWelcome, setShowWelcome] = useState(true);

  if (loading) {
    return (
      <ScreenShell label="Lesson" backHref={`/module/${moduleId}`} backLabel="Back to module">
        <LoadingState message="Getting your lesson ready..." />
      </ScreenShell>
    );
  }

  if (error || !data) {
    return (
      <ScreenShell label="Lesson" backHref={`/module/${moduleId}`} backLabel="Back to module">
        <ErrorState
          message={error?.message ?? "Could not load this lesson."}
          onRetry={reload}
        />
      </ScreenShell>
    );
  }

  const totalSections = data.sections.length;
  const hasSections = totalSections > 0;
  const sectionNumber = currentSection + 1;
  const progress = hasSections
    ? (sectionNumber / totalSections) * 100
    : 0;

  return (
    <ScreenShell
      label="Lesson"
      backHref={`/module/${moduleId}`}
      backLabel="Back to module"
    >
      {showWelcome && (
        <NovaBanner
          message="Welcome! Let's learn something new."
          onDismiss={() => setShowWelcome(false)}
        />
      )}

      <h1 className="mb-6 text-3xl font-bold">{data.title}</h1>

      {hasSections ? (
        <>
          <div className="mb-6">
            <p className="mb-2 text-sm font-bold">
              Section {sectionNumber} of {totalSections}
            </p>

            <div
              className="h-2 w-full overflow-hidden rounded-full bg-ink/10"
              role="progressbar"
              aria-label="Lesson progress"
              aria-valuemin={1}
              aria-valuemax={totalSections}
              aria-valuenow={sectionNumber}
            >
              <div
                className="h-full rounded-full bg-coral transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <LessonSection section={data.sections[currentSection]} />

          <div className="mt-6 flex items-center justify-between gap-4">
            <button
              type="button"
              disabled={currentSection === 0}
              onClick={() =>
                setCurrentSection((section) => section - 1)
              }
              className="rounded-lg border border-ink/20 px-5 py-3 font-bold disabled:opacity-40"
            >
              Previous
            </button>

            {currentSection < totalSections - 1 ? (
              <button
                type="button"
                onClick={() =>
                  setCurrentSection((section) => section + 1)
                }
                className="rounded-lg bg-coral px-5 py-3 font-bold text-white"
              >
                Next section
              </button>
            ) : (
              <Link
                href={`/quiz/${moduleId}`}
                className="rounded-lg bg-coral px-5 py-3 font-bold text-white"
              >
                Take the quiz
              </Link>
            )}
          </div>
        </>
      ) : (
        <div>
          <p className="mb-6">This lesson has no content yet.</p>
          <Link href={`/quiz/${moduleId}`} className="font-bold text-coral">
            Take the quiz
          </Link>
        </div>
      )}
    </ScreenShell>
  );
}
