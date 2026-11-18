type ProgressBarProps = {
  value: number;
  max: number;
  // Read out by screen readers, e.g. "Quiz progress".
  label: string;
};

// A thin bar showing how far through something the learner is.
// Callers render their own text (e.g. "Question 2 of 4") next to it.
export default function ProgressBar({ value, max, label }: ProgressBarProps) {
  // Clamp to 0-100 so the bar never overflows, and avoid NaN when max is 0.
  const percent =
    max > 0 ? Math.min(100, Math.max(0, (value / max) * 100)) : 0;

  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className="h-3 w-full overflow-hidden rounded-full border-2 border-ink bg-white"
    >
      <div
        className="h-full rounded-full bg-tealpop transition-all duration-300"
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}
