import type { SubmissionStatus } from "@/types/submission";

// Record<SubmissionStatus, ...> forces a style for EVERY status.
// If a status is ever added and forgotten here, TypeScript will complain.
const STYLES: Record<SubmissionStatus, { label: string; classes: string }> = {
  pending: { label: "Checking...", classes: "bg-cream" },
  passed: { label: "Passed!", classes: "bg-tealpop" },
  needs_revision: { label: "Needs revision", classes: "bg-coral" },
};

type StatusBadgeProps = {
  status: SubmissionStatus;
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const style = STYLES[status];

  return (
    <span
      className={`inline-block rounded-full border-2 border-ink px-3 py-1 font-display text-sm font-bold text-ink ${style.classes}`}
    >
      {style.label}
    </span>
  );
}