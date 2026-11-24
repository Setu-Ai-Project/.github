"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import DevSimulator from "@/app/components/progress/DevSimulator";
import SkillMap from "@/app/components/progress/SkillMap";
import { DEFAULT_POLL_MS, useProgressPolling } from "@/hooks/useProgressPolling";
import type { Skill } from "@/types/progress";

export default function SkillMapScreen() {
  const router = useRouter();
  const [refreshKey, setRefreshKey] = useState(0);
  const { data, error, loading } = useProgressPolling(DEFAULT_POLL_MS, refreshKey);

  function handleSelectSkill(skill: Skill) {
    router.push(`/module/${skill.moduleId}`);
  }

  return (
    <main className="min-h-screen bg-cream px-4 py-8 sm:px-6">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <div>
          <Link
            href="/dashboard"
            className="inline-block font-display text-sm font-bold text-coral hover:underline"
          >
            ← Back to dashboard
          </Link>
          <h1 className="mt-2 font-display text-3xl font-black text-ink sm:text-4xl">
            Skill Map
          </h1>
        </div>

        {loading && !data && (
          <div
            role="status"
            className="w-full rounded-2xl border-4 border-ink bg-white p-6 shadow-[4px_4px_0_#172A32]"
          >
            <p className="font-display font-bold text-ink">
              Getting your skill map ready...
            </p>
          </div>
        )}

        {error && !data && (
          <div
            role="alert"
            className="w-full rounded-2xl border-4 border-coral bg-white p-6 shadow-[4px_4px_0_#172A32]"
          >
            <p className="font-display font-bold text-ink">
              We could not load your skill map.
            </p>
            <button
              type="button"
              onClick={() => setRefreshKey((k) => k + 1)}
              className="mt-4 rounded-xl border-2 border-ink bg-coral px-4 py-2 font-display text-sm font-bold text-white shadow-[2px_2px_0_#172A32] hover:-translate-y-0.5 active:translate-y-0"
            >
              Try again
            </button>
          </div>
        )}

        {data && (
          <div className="flex flex-col gap-4">
            {error && (
              <p className="text-xs font-bold text-taskgray">
                Having trouble updating. Showing your last progress.
              </p>
            )}
            <SkillMap skills={data.skills} onSelectSkill={handleSelectSkill} />
          </div>
        )}

        <div className="mt-4">
          <DevSimulator />
        </div>
      </div>
    </main>
  );
}
