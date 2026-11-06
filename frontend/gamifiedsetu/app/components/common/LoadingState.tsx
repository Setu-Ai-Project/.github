type LoadingStateProps = {
  message?: string;
};

export default function LoadingState({
  message = "Getting things ready...",
}: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-label={message}
      className="w-full animate-pulse space-y-4 rounded-2xl border border-ink/10 bg-white p-6"
    >
      <p className="font-bold text-ink">{message}</p>

      <div className="h-4 w-3/4 rounded-full bg-taskgray/20" />
      <div className="h-4 w-full rounded-full bg-taskgray/20" />
      <div className="h-4 w-5/6 rounded-full bg-taskgray/20" />
    </div>
  );
}