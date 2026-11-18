"use client";

import BugTooltip from "@/app/components/mascots/BugTooltip";
import SparkCard from "@/app/components/mascots/SparkCard";
import type { QuizMascotKind } from "@/utils/quizReducer";

type QuizMascotProps = {
  kind: QuizMascotKind;
  score: number;
  total: number;
  onDismiss: () => void;
};

// Picks the right mascot and message for each quiz moment.
// The parent gives it a new `key` per moment, so each one appears fresh.
export default function QuizMascot({ kind, score, total, onDismiss }: QuizMascotProps) {
  if (kind === "wrong") {
    return (
      <BugTooltip
        message="Oops, close! Read the explanation and keep going."
        onDismiss={onDismiss}
      />
    );
  }

  const message = kind === "correct" ? "Nice one!" : `You scored ${score} of ${total}!`;
  return <SparkCard message={message} onDismiss={onDismiss} />;
}
