"use client";

import SubmitButton from "@/app/components/submission/SubmitButton";
import FeedbackList from "@/app/components/submission/FeedbackList";

export default function SubmissionUiTestPage() {
  return (
    <main className="min-h-screen bg-cream p-8">
      <h1 className="mb-6 font-display text-3xl font-bold text-ink">
        SubmitButton + FeedbackList Test
      </h1>

      <div className="flex flex-col items-start gap-6">
        <SubmitButton
          onClick={() => console.log("Submit clicked")}
          loading={false}
        />
        <SubmitButton onClick={() => {}} loading={true} />
        <SubmitButton onClick={() => {}} loading={false} disabled />

        <FeedbackList
          items={[
            "Your answer is missing the loop condition.",
            "Hint: check that your counter actually increases.",
          ]}
        />
      </div>
    </main>
  );
}