
"use client";

import { useState } from "react";

type HintListProps = {
  hints: string[];
  onReveal?: (shownCount: number) => void;
};

export default function HintList({
  hints,
  onReveal,
}: HintListProps) {
  const [shownCount, setShownCount] = useState(0);

  const showNextHint = () => {
    const nextCount = shownCount + 1;

    setShownCount(nextCount);
    onReveal?.(nextCount);
  };

  if (hints.length === 0) {
    return <p>No hints for this challenge.</p>;
  }

  return (
    <div className="space-y-4">
      <ol className="space-y-3">
        {hints.slice(0, shownCount).map((hint, index) => (
          <li
            key={index}
            className="rounded-xl border border-ink/10 bg-white p-4"
          >
            <p className="mb-1 font-bold">Hint {index + 1}</p>
            <p className="whitespace-pre-line break-words">{hint}</p>
          </li>
        ))}
      </ol>

      <p className="text-sm text-ink/60">
        {shownCount} of {hints.length} hints shown
      </p>

      <button
        type="button"
        onClick={showNextHint}
        disabled={shownCount >= hints.length}
        className="rounded-lg bg-coral px-4 py-2 font-bold text-white disabled:opacity-50"
      >
        {shownCount >= hints.length ? "No more hints" : "Show next hint"}
      </button>
    </div>
  );
}
