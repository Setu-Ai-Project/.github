
"use client";

import { useState } from "react";
import MyDoubts from "@/app/components/mentor-mode/MyDoubts";
import { resetMockDoubts } from "@/api/mockDoubtApi";

export default function LearnerDoubtsTestPage() {
  const [resetKey, setResetKey] = useState(0);

  function handleClearAll() {
    resetMockDoubts();
    setResetKey((key) => key + 1);
  }

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 p-4 sm:p-6">
      <header className="space-y-3">
        <h1 className="text-2xl font-bold text-gray-900">
          Learner Doubts Test
        </h1>

        <p className="text-sm text-gray-600">
          Test submitting doubts and viewing mentor replies.
        </p>

        <button
          type="button"
          onClick={handleClearAll}
          className="rounded-lg border border-red-300 px-4 py-2 font-medium text-red-700 hover:bg-red-50"
        >
          Clear all doubts
        </button>
      </header>

      <MyDoubts key={resetKey} />
    </main>
  );
}
