"use client";
import { useState } from "react";

import {
  checkAnswer,
  getBuilderChallenge,
  getLearnContent,
  getQuiz,
} from "@/api/learningApi";

export default function LearningApiTestPage() {
  const [result, setResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

    async function runTest(test: () => Promise<unknown>) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await test();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-cream p-6 text-ink">
    
    <div className="mx-auto max-w-2xl">
  <h1 className="font-display text-3xl font-bold">
    Learning API Test
  </h1>

  <div className="mt-6 flex flex-wrap gap-3">
    <button
      onClick={() => runTest(() => getLearnContent("1"))}
      className="rounded-lg bg-coral px-4 py-2 font-bold text-white"
    >
      Load lesson
    </button>

    <button
      onClick={() => runTest(() => getQuiz("1"))}
      className="rounded-lg bg-coral px-4 py-2 font-bold text-white"
    >
      Load quiz
    </button>

    <button
      onClick={() => runTest(() => getBuilderChallenge("1"))}
      className="rounded-lg bg-coral px-4 py-2 font-bold text-white"
    >
      Load challenge
    </button>

    <button
      onClick={() => runTest(() => checkAnswer("1", "1", 0))}
      className="rounded-lg bg-tealpop px-4 py-2 font-bold text-white"
    >
      Check quiz answer 1
    </button>
  </div>
  {loading && (
  <p className="mt-4 font-bold">Loading...</p>
)}
{error && (
  <div className="mt-4 rounded-lg border border-coral bg-white p-4 text-coral">
    {error}
  </div>
)}
{result !== null && (
  <pre className="mt-4 overflow-x-auto rounded-lg border border-ink/10 bg-white p-4 text-sm">
    {JSON.stringify(result, null, 2)}
  </pre>
)}
</div>
    </main>
  );
}


