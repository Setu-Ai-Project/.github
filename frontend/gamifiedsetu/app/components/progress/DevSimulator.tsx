"use client";

import { useState } from "react";

import { getMockProgress, simulateCompleteChallenge } from "@/api/mockProgress";
import { buttonClass } from "@/app/components/common/buttonStyles";

// Only shown while developing with mock data; never in production.
function isEnabled(): boolean {
  return (
    process.env.NODE_ENV === "development" &&
    process.env.NEXT_PUBLIC_USE_MOCK === "true"
  );
}

// DEV ONLY: pretends the learner finished a skill, so live updates can be tested
// without a backend. It changes the mock directly; the page catches up on its next poll.
export default function DevSimulator() {
  const [selectedId, setSelectedId] = useState("");
  const [message, setMessage] = useState("");
  // Bumped after each click so the dropdown re-reads the in-progress skills.
  const [, setVersion] = useState(0);

  if (!isEnabled()) return null;

  const inProgress = getMockProgress().skills.filter(
    (skill) => skill.status === "in-progress"
  );
  // Fall back to the first skill if nothing (or a now-completed skill) is selected.
  const chosenId = inProgress.some((skill) => skill.id === selectedId)
    ? selectedId
    : (inProgress[0]?.id ?? "");

  function handleSimulate() {
    const done = simulateCompleteChallenge(chosenId);
    setMessage(
      done
        ? "Done! The page updates on the next poll (within 5 seconds)."
        : "That skill can't be completed right now."
    );
    setVersion((version) => version + 1);
  }

  return (
    <section className="rounded-2xl border-4 border-dashed border-coral bg-white p-4">
      <p className="mb-3 inline-block rounded-full border-2 border-ink bg-coral px-3 py-1 font-display text-xs font-bold text-ink">
        DEV ONLY
      </p>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="flex flex-1 flex-col gap-1 font-display text-sm font-bold text-ink">
          Skill to complete
          <select
            value={chosenId}
            onChange={(event) => setSelectedId(event.target.value)}
            disabled={inProgress.length === 0}
            className="rounded-xl border-2 border-ink bg-cream p-2 font-sans font-normal"
          >
            {inProgress.map((skill) => (
              <option key={skill.id} value={skill.id}>
                {skill.name}
              </option>
            ))}
          </select>
        </label>

        <button
          type="button"
          onClick={handleSimulate}
          disabled={!chosenId}
          className={buttonClass("coral")}
        >
          Simulate: complete challenge
        </button>
      </div>

      {message && (
        <p role="status" className="mt-3 text-sm text-ink">
          {message}
        </p>
      )}
    </section>
  );
}
