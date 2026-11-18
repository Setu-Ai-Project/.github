"use client";

import ProgressBar from "@/app/components/common/ProgressBar";
import { buttonClass } from "@/app/components/common/buttonStyles";
import { useQuiz } from "@/hooks/useQuiz";
import type { Quiz } from "@/types/learning";
import QuizMascot from "./QuizMascot";
import QuizQuestionCard from "./QuizQuestionCard";
import QuizResult from "./QuizResult";

type QuizPlayerProps = {
  quiz: Quiz;
  moduleId: string;
};

// Plays a loaded quiz: one question at a time, then the results.
// All the rules live in useQuiz; this component only draws them.
export default function QuizPlayer({ quiz, moduleId }: QuizPlayerProps) {
  const {
    state,
    question,
    total,
    isLast,
    mascot,
    select,
    check,
    next,
    dismissMascot,
    restart,
  } = useQuiz(moduleId, quiz.questions);

  // A new key per moment makes each mascot appear fresh.
  const mascotNode = mascot && (
    <QuizMascot
      key={`${state.currentIndex}-${mascot}`}
      kind={mascot}
      score={state.score}
      total={total}
      onDismiss={dismissMascot}
    />
  );

  const title = (
    <h1 className="break-words font-display text-3xl font-bold">{quiz.title}</h1>
  );

  if (state.finished) {
    return (
      <div className="flex flex-col gap-6">
        {title}
        {mascotNode}
        <QuizResult score={state.score} total={total} moduleId={moduleId} onRetry={restart} />
      </div>
    );
  }

  if (!question) return null;

  const result = state.checkResult;
  const questionNumber = state.currentIndex + 1;

  return (
    <div className="flex flex-col gap-6">
      {title}

      <div className="flex flex-col gap-2">
        <p className="font-display text-sm font-bold">
          Question {questionNumber} of {total}
        </p>
        <ProgressBar value={questionNumber} max={total} label="Quiz progress" />
      </div>

      <QuizQuestionCard
        key={question.id}
        question={question}
        selectedIndex={state.selectedIndex}
        onSelect={select}
        isChecked={result !== null}
        correctIndex={result?.correctIndex}
      />

      {/* aria-live lets screen readers announce the feedback as it appears. */}
      <div aria-live="polite" className="flex flex-col gap-2">
        {result && (
          <>
            <p className="font-display text-lg font-bold">
              {result.correct ? "Correct!" : "Not quite."}
            </p>
            {result.explanation && <p>{result.explanation}</p>}
          </>
        )}
        {state.checkFailed && (
          <p className="rounded-xl border-2 border-coral bg-cream p-3 font-bold">
            We could not check your answer. Please try again.
          </p>
        )}
      </div>

      {mascotNode}

      <div>
        {result ? (
          <button type="button" onClick={next} className={buttonClass("teal")}>
            {isLast ? "See results" : "Next question"}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => void check()}
            disabled={state.selectedIndex === null || state.checking}
            className={buttonClass("teal")}
          >
            {state.checking ? "Checking..." : "Check answer"}
          </button>
        )}
      </div>
    </div>
  );
}
