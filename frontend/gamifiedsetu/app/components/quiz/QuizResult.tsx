import Link from "next/link";

import { buttonClass } from "@/app/components/common/buttonStyles";

type QuizResultProps = {
  score: number;
  total: number;
  moduleId: string;
  onRetry: () => void;
};

// A kind message that depends on how well the learner did. Never harsh.
function resultMessage(score: number, total: number): string {
  if (score === total) return "Perfect score! You really know this.";
  if (score >= total / 2) {
    return "Great work! Review the ones you missed and you will have it.";
  }
  return "Good effort! Every expert started here. Try again and you will improve.";
}

// The results card shown when the quiz is finished.
export default function QuizResult({ score, total, moduleId, onRetry }: QuizResultProps) {
  return (
    <section className="rounded-2xl border-4 border-ink bg-white p-4 shadow-[8px_8px_0_#172A32] sm:p-6">
      <h2 className="font-display text-2xl font-bold text-ink">Quiz complete!</h2>
      <p className="mt-2 font-display text-3xl font-black text-ink">
        You scored {score} of {total}
      </p>
      <p className="mt-2 text-ink">{resultMessage(score, total)}</p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button type="button" onClick={onRetry} className={buttonClass("white")}>
          Try again
        </button>
        <Link href={`/challenge/${moduleId}`} className={buttonClass("coral")}>
          Continue to challenge
        </Link>
      </div>
    </section>
  );
}
