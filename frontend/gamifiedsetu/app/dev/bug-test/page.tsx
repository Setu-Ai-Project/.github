"use client";

import BugTooltip from "../../components/mascots/BugTooltip";

export default function BugTestPage() {
  return (
    <main className="min-h-screen bg-cream p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          BugTooltip Test
        </h1>

        <BugTooltip
          message="Careful, you're missing a step!"
          onDismiss={() => console.log("First BugTooltip dismissed")}
        />

        <BugTooltip
          message="Double-check that answer before submitting."
          onDismiss={() => console.log("Second BugTooltip dismissed")}
        />
      </div>
    </main>
  );
}