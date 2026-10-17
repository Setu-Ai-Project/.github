"use client";

import { useMode } from "@/context/ModeContext";
import type { Mode } from "@/types/doubt";

const OPTIONS: { value: Mode; label: string }[] = [
  { value: "learner", label: "Learner" },
  { value: "mentor", label: "Mentor" },
];

// UI-only switch for development. A real mentor role check is still needed before launch.
export default function ModeSwitch() {
  const { mode, setMode } = useMode();

  return (
    <div
      role="group"
      aria-label="Switch mode"
      className="inline-flex gap-1 rounded-full border-4 border-ink bg-white p-1 shadow-[4px_4px_0_#172A32]"
    >
      {OPTIONS.map((option) => {
        const active = mode === option.value;
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => setMode(option.value)}
            aria-pressed={active}
            className={`rounded-full px-4 py-1 font-display text-sm font-bold text-ink transition-colors ${
              active ? "bg-tealpop" : "hover:bg-cream"
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
