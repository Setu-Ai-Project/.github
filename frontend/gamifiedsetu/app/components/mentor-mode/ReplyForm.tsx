"use client";

import { useRef, useState } from "react";

type ReplyFormProps = {
  replyTo: string; // the question being answered, used for the accessible label
  onSend: (text: string) => Promise<void>; // should throw if sending failed
};

export default function ReplyForm({ replyTo, onSend }: ReplyFormProps) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const inFlight = useRef(false); // blocks a double-click from sending twice

  async function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || inFlight.current) return;

    inFlight.current = true;
    setSending(true);
    setError("");
    try {
      await onSend(trimmed);
      setText("");
    } catch {
      setError("We could not send your reply. Please try again."); // keep their text
    } finally {
      inFlight.current = false;
      setSending(false);
    }
  }

  return (
    <div className="space-y-2">
      {/* Stacks on phones, sits side by side on wider screens. */}
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          aria-label={`Reply to: ${replyTo}`}
          className="min-w-0 flex-1 rounded-xl border-2 border-ink bg-cream p-2 text-ink placeholder:text-taskgray focus:outline-none focus:ring-2 focus:ring-tealpop disabled:opacity-60"
          placeholder="Write a reply..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={sending}
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={sending || text.trim() === ""}
          className="rounded-2xl border-4 border-ink bg-tealpop px-4 py-2 font-display font-bold text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
        >
          {sending ? "Sending..." : "Send reply"}
        </button>
      </div>
      {error && (
        <p className="rounded-xl border-2 border-coral bg-cream p-2 text-sm font-bold text-ink">
          {error}
        </p>
      )}
    </div>
  );
}
