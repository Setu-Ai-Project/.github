"use client";

import { useState } from "react";
import { createDoubt } from "@/api/doubtApi";
import { resetMockDoubts } from "@/api/mockDoubtApi";
import MentorDashboard from "@/app/components/mentor-mode/MentorDashboard";

const SAMPLE_QUESTIONS = [
  "How do I stop an infinite loop?",
  "What is the difference between = and ==?",
  "Why does my function return undefined?",
  "What does AI training data mean?",
];

export default function MentorDashboardTestPage() {
  // Changing the key mounts a fresh MentorDashboard, which reloads the queue.
  const [version, setVersion] = useState(0);
  const [adding, setAdding] = useState(false);

  async function addSample() {
    setAdding(true);
    const question =
      SAMPLE_QUESTIONS[Math.floor(Math.random() * SAMPLE_QUESTIONS.length)];
    await createDoubt(question, "Sample Learner");
    setAdding(false);
    setVersion((v) => v + 1);
  }

  function clearAll() {
    resetMockDoubts();
    setVersion((v) => v + 1);
  }

  return (
    <main className="min-h-screen bg-cream px-4 py-10">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          Mentor Dashboard Test
        </h1>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={addSample}
            disabled={adding}
            className="rounded-full border-2 border-ink bg-white px-4 py-1 font-bold text-ink disabled:opacity-50"
          >
            {adding ? "Adding..." : "Add sample doubt"}
          </button>
          <button
            type="button"
            onClick={clearAll}
            className="rounded-full border-2 border-ink bg-white px-4 py-1 font-bold text-ink"
          >
            Clear all doubts
          </button>
        </div>
        <MentorDashboard key={version} />
      </div>
    </main>
  );
}
