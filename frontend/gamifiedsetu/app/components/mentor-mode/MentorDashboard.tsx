"use client";

import { useEffect, useState } from "react";
import { listDoubts, replyToDoubt } from "@/api/doubtApi";
import type { Doubt, DoubtStatus } from "@/types/doubt";
import DoubtCard from "./DoubtCard";
import ReplyForm from "./ReplyForm";

// Until login is wired in, every reply is sent as this test mentor.
export const TEST_MENTOR_NAME = "Test Mentor";

const TABS: { value: DoubtStatus; label: string }[] = [
  { value: "open", label: "Open" },
  { value: "answered", label: "Answered" },
];

export default function MentorDashboard() {
  const [doubts, setDoubts] = useState<Doubt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<DoubtStatus>("open");
  // Bump this number to reload the queue (e.g. after a reply).
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false; // ignore a late answer if the dashboard has disappeared

    listDoubts()
      .then((list) => {
        if (ignore) return;
        setDoubts(list);
        setError("");
      })
      .catch(() => {
        if (!ignore) setError("We could not load the doubts. Please refresh the page.");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [reloadKey]);

  // Passed to each ReplyForm. If replyToDoubt throws, ReplyForm shows its own error.
  async function sendReply(id: string, text: string) {
    await replyToDoubt(id, text, TEST_MENTOR_NAME);
    setReloadKey((key) => key + 1);
  }

  if (loading) return <p className="text-taskgray">Loading doubts...</p>;

  if (error) {
    return (
      <p className="rounded-xl border-2 border-coral bg-white p-3 font-bold text-ink">
        {error}
      </p>
    );
  }

  // Only the selected tab, oldest first, so whoever waited longest is helped first.
  const shown = doubts
    .filter((d) => d.status === tab)
    .sort((a, b) => a.createdAt.localeCompare(b.createdAt));

  return (
    <div className="space-y-4">
      <div role="group" aria-label="Filter doubts" className="flex flex-wrap gap-2">
        {TABS.map((t) => {
          const count = doubts.filter((d) => d.status === t.value).length;
          const active = tab === t.value;
          return (
            <button
              key={t.value}
              type="button"
              onClick={() => setTab(t.value)}
              aria-pressed={active}
              className={`rounded-full border-2 border-ink px-4 py-1 font-display text-sm font-bold text-ink ${
                active ? "bg-tealpop" : "bg-white hover:bg-cream"
              }`}
            >
              {t.label} ({count})
            </button>
          );
        })}
      </div>

      {shown.length === 0 && <p className="text-taskgray">Nothing here yet.</p>}

      <div className="space-y-6">
        {shown.map((doubt) => (
          <div key={doubt.id} className="space-y-2">
            <DoubtCard doubt={doubt} />
            {doubt.status === "open" && (
              <ReplyForm
                replyTo={doubt.question}
                onSend={(text) => sendReply(doubt.id, text)}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
