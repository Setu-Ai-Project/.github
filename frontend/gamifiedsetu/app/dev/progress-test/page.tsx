"use client";

import { resetMockProgress } from "@/api/mockProgress";
import { buttonClass } from "@/app/components/common/buttonStyles";
import DevSimulator from "@/app/components/progress/DevSimulator";
import { useProgressPolling } from "@/hooks/useProgressPolling";

export default function ProgressTestPage() {
  const { data, error, loading } = useProgressPolling();

  return (
    <main className="min-h-screen bg-cream p-6 text-ink">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold">Progress Test</h1>

        <DevSimulator />

        <div>
          <button
            type="button"
            onClick={resetMockProgress}
            className={buttonClass("white")}
          >
            Reset mock
          </button>
        </div>

        {loading && <p className="font-bold">Loading...</p>}

        {error && (
          <p className="rounded-xl border-2 border-coral bg-white p-3 font-bold">
            {error.message}
          </p>
        )}

        {data && (
          <pre className="overflow-x-auto rounded-xl border-2 border-ink bg-white p-4 text-sm">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </div>
    </main>
  );
}
