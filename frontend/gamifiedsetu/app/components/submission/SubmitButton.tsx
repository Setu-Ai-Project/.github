"use client";

type SubmitButtonProps = {
  onClick: () => void;
  loading: boolean;
  disabled?: boolean;
};

export default function SubmitButton({
  onClick,
  loading,
  disabled = false,
}: SubmitButtonProps) {
  const isDisabled = loading || disabled;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isDisabled}
      className="rounded-2xl border-4 border-ink bg-coral px-6 py-3 font-display font-bold text-ink shadow-[4px_4px_0_#172A32] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
    >
      {loading ? "Checking..." : "Submit"}
    </button>
  );
}