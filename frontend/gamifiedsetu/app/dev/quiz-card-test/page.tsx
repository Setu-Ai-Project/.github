"use client";

import { useState } from "react";

import QuizQuestionCard from "@/app/components/quiz/QuizQuestionCard";
import QuizResult from "@/app/components/quiz/QuizResult";
import type { QuizQuestion } from "@/types/learning";

const QUESTION: QuizQuestion = {
  id: "dev-q1",
  question: "Which of these uses AI?",
  options: ["A calculator", "A photo app that spots faces", "A light switch"],
};

export default function QuizCardTestPage() {
  // The first card is clickable, so it keeps its own selection.
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  return (
    <main className="min-h-screen bg-cream p-6 text-ink">
      <div className="mx-auto flex max-w-2xl flex-col gap-8">
        <h1 className="font-display text-3xl font-bold">Quiz Card Test</h1>

        <section className="flex flex-col gap-2">
          <h2 className="font-display text-lg font-bold">Clickable, not checked</h2>
          <QuizQuestionCard
            question={QUESTION}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
            isChecked={false}
          />
        </section>

        <section className="flex flex-col gap-2">
          <h2 className="font-display text-lg font-bold">Checked: wrong pick</h2>
          <QuizQuestionCard
            question={{ ...QUESTION, id: "dev-q2" }}
            selectedIndex={0}
            onSelect={() => {}}
            isChecked={true}
            correctIndex={1}
          />
        </section>

        <section className="flex flex-col gap-2">
          <h2 className="font-display text-lg font-bold">Result: 2 of 4</h2>
          <QuizResult
            score={2}
            total={4}
            moduleId="1"
            onRetry={() => console.log("Try again clicked")}
          />
        </section>
      </div>
    </main>
  );
}
