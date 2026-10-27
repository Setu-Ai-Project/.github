import SubmissionPanel from "@/app/components/submission/SubmissionPanel";

export default function SubmissionDemoPage() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-6 bg-cream px-4 py-10">
      <h1 className="font-display text-3xl font-bold text-ink">
        Submission Demo
      </h1>

      <p className="max-w-xl text-center text-taskgray">
        Type <strong>correct</strong> to pass. Anything else needs revision.
      </p>

      <SubmissionPanel challengeId="test-challenge-1" />
    </main>
  );
}