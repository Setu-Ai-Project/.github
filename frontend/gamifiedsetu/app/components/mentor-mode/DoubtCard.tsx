import type { Doubt } from "@/types/doubt";

type DoubtCardProps = {
  doubt: Doubt;
};

export default function DoubtCard({ doubt }: DoubtCardProps) {
  const isOpen = doubt.status === "open";
  const badgeText = isOpen ? "Open" : "Answered";
  const badgeBg = isOpen ? "bg-cream" : "bg-tealpop";

  return (
    <article className="w-full max-w-full rounded-2xl border-2 border-ink bg-white p-5 shadow-[4px_4px_0_#172A32]">
      {/* Top row: Status Badge & Learner Attribution */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span
          className={`inline-block rounded-full border-2 border-ink px-3 py-1 font-display text-sm font-bold text-ink ${badgeBg}`}
        >
          {badgeText}
        </span>
        <span className="text-xs font-sans text-taskgray">
          Asked by {doubt.learnerName}
        </span>
      </div>

      {/* Question */}
      <h3 className="mt-3 font-display text-lg font-bold text-ink break-words [overflow-wrap:anywhere]">
        {doubt.question}
      </h3>

      {/* Reply or Waiting section */}
      <div className="mt-4">
        {doubt.reply ? (
          <div className="rounded-xl border-2 border-ink bg-cream p-4">
            <p className="font-display text-sm font-bold text-ink">
              {doubt.reply.mentorName} says:
            </p>
            <p className="mt-1 text-sm text-ink break-words [overflow-wrap:anywhere]">
              {doubt.reply.text}
            </p>
          </div>
        ) : (
          <p className="text-sm italic text-taskgray">
            Waiting for a mentor to reply...
          </p>
        )}
      </div>
    </article>
  );
}
