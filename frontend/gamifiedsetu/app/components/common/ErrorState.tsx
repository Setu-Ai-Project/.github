"use client";

type ErrorStateProps = {
  message?: string;
  onRetry: () => void;
};

export default function ErrorState({
  message = "We could not load this right now. Please try again.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="w-full rounded-2xl border border-coral/30 bg-white p-6"
    >
      <p className="font-bold text-ink">{message}</p>

      <button
        type="button"
        onClick={onRetry}
        className="mt-4 rounded-lg bg-coral px-4 py-2 font-bold text-white"
      >
        Try again
      </button>
    </div>
  );
}