"use client";

import { useState } from "react";
import BugTooltip from "../../components/mascots/BugTooltip";
import { checkBugMistakes, BugMistake } from "@/api/aiApi";

export default function BugTestPage() {
  const [inputText, setInputText] = useState("");
  const [detectedMistakes, setDetectedMistakes] = useState<BugMistake[]>([]);
  const [isChecking, setIsChecking] = useState(false);

  const handleCheck = async () => {
    setIsChecking(true);
    try {
      const results = await checkBugMistakes(inputText);
      setDetectedMistakes(results);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <main className="min-h-screen bg-cream p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          Bug Mascot & AI Mistake Detection Test
        </h1>

        <section className="rounded-2xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32]">
          <h2 className="font-display text-xl font-bold text-ink mb-2">
            Live AI Research Mistake Checker
          </h2>
          <p className="text-sm text-ink/70 mb-4">
            Type an answer below (try &quot;draw something nice&quot;) to trigger Bug&apos;s
            real-time mistake detection:
          </p>

          <div className="flex flex-col gap-3">
            <textarea
              className="w-full rounded-xl border-2 border-ink bg-cream p-3 font-sans text-ink focus:outline-none focus:ring-2 focus:ring-coral"
              rows={3}
              placeholder="e.g. Please draw something nice for my game"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            <button
              onClick={handleCheck}
              disabled={isChecking || !inputText.trim()}
              className="self-start rounded-xl border-2 border-ink bg-coral px-4 py-2 font-display font-bold text-ink shadow-[4px_4px_0_#172A32] transition hover:-translate-y-0.5 disabled:opacity-50"
            >
              {isChecking ? "Checking with Bug..." : "Check with Bug Mascot"}
            </button>
          </div>

          <div className="mt-4 flex flex-col gap-3">
            {detectedMistakes.map((m) => (
              <BugTooltip
                key={m.id}
                message={`${m.explanation} Hint: ${m.fixHint}`}
                onDismiss={() => {
                  setDetectedMistakes((prev) => prev.filter((item) => item.id !== m.id));
                }}
              />
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="font-display text-xl font-bold text-ink">Static Examples</h2>
          <BugTooltip
            message="Careful, you're missing a step!"
            onDismiss={() => console.log("First BugTooltip dismissed")}
          />

          <BugTooltip
            message="Double-check that answer before submitting."
            onDismiss={() => console.log("Second BugTooltip dismissed")}
          />
        </section>
      </div>
    </main>
  );
}
