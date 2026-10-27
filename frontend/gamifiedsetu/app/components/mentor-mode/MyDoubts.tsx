
"use client";

import { useEffect, useState } from "react";
import { listDoubts } from "@/api/doubtApi";
import type { Doubt } from "@/types/doubt";
import AskDoubtForm from "./AskDoubtForm";
import DoubtCard from "./DoubtCard";

export default function MyDoubts() {
  const [doubts, setDoubts] = useState<Doubt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadDoubts() {
      try {
        const result = await listDoubts();

        if (cancelled) return;

        setDoubts(result);
        setError("");
      } catch {
        if (cancelled) return;

        setError(
          "We could not load your doubts. Please refresh the page."
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDoubts();

    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  const sortedDoubts = [...doubts].sort(
    (a, b) =>
      new Date(b.createdAt).getTime() -
      new Date(a.createdAt).getTime()
  );

  function handleDoubtSent() {
    setLoading(true);
    setReloadKey((key) => key + 1);
  }

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 p-4 sm:p-6">
      <AskDoubtForm onSent={handleDoubtSent} />

      <section className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">
          My doubts
        </h1>

        {loading && (
          <p role="status">Loading your doubts...</p>
        )}

        {!loading && error && (
          <p
            role="alert"
            className="rounded-lg border border-[#F08080] p-3 text-red-700"
          >
            {error}
          </p>
        )}

        {!loading && !error && sortedDoubts.length === 0 && (
          <p>No doubts yet. Ask your first one above!</p>
        )}

        {!loading &&
          !error &&
          sortedDoubts.map((doubt) => (
            <DoubtCard key={doubt.id} doubt={doubt} />
          ))}
      </section>
    </main>
  );
}
