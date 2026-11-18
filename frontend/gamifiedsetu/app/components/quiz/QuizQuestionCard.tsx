"use client";

import type { QuizQuestion } from "@/types/learning";

type QuizQuestionCardProps = {
  question: QuizQuestion;
  selectedIndex: number | null;
  onSelect: (index: number) => void;
  // True once the answer has been checked: options lock and show right/wrong.
  isChecked: boolean;
  // The right option, from checkAnswer(). Never read from question.correctIndex.
  correctIndex?: number;
};

type OptionLook = "idle" | "selected" | "correct" | "wrong";

const OPTION_CLASSES: Record<OptionLook, string> = {
  idle: "border-2 bg-white",
  selected: "border-4 bg-cream",
  correct: "border-4 bg-tealpop",
  wrong: "border-4 bg-coral",
};

// Text labels, so colour is never the only signal.
const OPTION_BADGES: Partial<Record<OptionLook, string>> = {
  correct: "Correct",
  wrong: "Not quite",
};

function optionLook(
  index: number,
  selectedIndex: number | null,
  isChecked: boolean,
  correctIndex?: number
): OptionLook {
  if (isChecked && correctIndex !== undefined) {
    if (index === correctIndex) return "correct";
    if (index === selectedIndex) return "wrong";
    return "idle";
  }
  return index === selectedIndex ? "selected" : "idle";
}

// One quiz question with its options. Display only: the parent owns all state.
export default function QuizQuestionCard({
  question,
  selectedIndex,
  onSelect,
  isChecked,
  correctIndex,
}: QuizQuestionCardProps) {
  return (
    <div className="rounded-2xl border-4 border-ink bg-white p-4 shadow-[8px_8px_0_#172A32] sm:p-6">
      {/* fieldset + legend make the options one named group for screen readers.
          min-w-0 stops very long words from stretching the card. */}
      <fieldset className="min-w-0">
        <legend className="mb-4 break-words font-display text-xl font-bold text-ink">
          {question.question}
        </legend>

        <div className="flex flex-col gap-3">
          {question.options.map((option, index) => {
            const look = optionLook(index, selectedIndex, isChecked, correctIndex);
            const badge = OPTION_BADGES[look];

            return (
              // Real radio inputs give keyboard users Tab + arrow keys for free.
              <label
                key={index}
                className={`flex min-h-12 items-center gap-3 rounded-xl border-ink p-3 text-ink focus-within:ring-2 focus-within:ring-coral ${OPTION_CLASSES[look]} ${isChecked ? "cursor-default" : "cursor-pointer"}`}
              >
                <input
                  type="radio"
                  name={question.id}
                  checked={selectedIndex === index}
                  onChange={() => onSelect(index)}
                  disabled={isChecked}
                  className="h-5 w-5 shrink-0 accent-ink"
                />
                <span className="min-w-0 flex-1 break-words">{option}</span>
                {badge && (
                  <span className="shrink-0 rounded-full border-2 border-ink bg-white px-2 py-0.5 font-display text-xs font-bold">
                    {badge}
                  </span>
                )}
              </label>
            );
          })}
        </div>
      </fieldset>
    </div>
  );
}
