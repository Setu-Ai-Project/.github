
"use client";

import { useRef, useState } from "react";
import { createDoubt } from "@/api/doubtApi";

export const TEST_LEARNER_NAME = "Test Learner";

type AskDoubtFormProps = {
  onSent: () => void;
};

export default function AskDoubtForm({ onSent }: AskDoubtFormProps) {
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState("");
  const [hasError, setHasError] = useState(false);

  const inFlight = useRef(false);

  async function handleSend() {
    if (inFlight.current) return;

    const trimmedQuestion = question.trim();

    if (trimmedQuestion.length < 5) {
      setHasError(true);
      setMessage("Please describe your doubt in a few words.");
      return;
    }

    inFlight.current = true;
    setSending(true);
    setMessage("");
    setHasError(false);

    try {
      await createDoubt(trimmedQuestion, TEST_LEARNER_NAME);

      setQuestion("");
      setHasError(false);
      setMessage("Doubt sent! A mentor will reply soon.");
      onSent();
    } catch {
      setHasError(true);
      setMessage("We could not send your doubt. Please try again.");
    } finally {
      inFlight.current = false;
      setSending(false);
    }
  }

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <label
        htmlFor="learner-doubt"
        className="mb-2 block font-medium text-gray-900"
      >
        Ask a doubt
      </label>

      <textarea
        id="learner-doubt"
        placeholder="What are you stuck on?"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        disabled={sending}
        className="w-full resize-y rounded-lg border border-gray-300 p-3 text-gray-900 placeholder:text-gray-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-100"
      />

      <button
        type="button"
        onClick={handleSend}
        disabled={sending}
        className="mt-3 rounded-lg bg-teal-700 px-5 py-2.5 font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {sending ? "Sending..." : "Send doubt"}
      </button>

      {message && (
        <p
          role="status"
          aria-live="polite"
          className={`mt-3 rounded-lg p-3 text-sm ${
            hasError
              ? "border border-[#F08080] bg-white text-red-700"
              : "text-teal-800"
          }`}
        >
          {message}
        </p>
      )}
    </section>
  );
}
