import DoubtCard from "@/app/components/mentor-mode/DoubtCard";
import type { Doubt } from "@/types/doubt";

export default function DoubtCardTestPage() {
  const exampleOpenDoubt: Doubt = {
    id: "doubt-1",
    learnerName: "Aarav",
    question: "How do I stop an infinite loop?",
    status: "open",
    createdAt: "2026-10-12T10:00:00Z",
  };

  const exampleAnsweredDoubt: Doubt = {
    id: "doubt-2",
    learnerName: "Zoya",
    question: "How does the useState hook work in React?",
    status: "answered",
    createdAt: "2026-10-12T09:30:00Z",
    reply: {
      mentorName: "Test Mentor",
      text: "useState lets you declare a state variable that React remembers between renders.",
      repliedAt: "2026-10-12T09:45:00Z",
    },
  };

  const exampleLongDoubt: Doubt = {
    id: "doubt-3",
    learnerName: "Jordan",
    question:
      "WhyDoesMyFunctionFailWhenCallingSuperUltraLongFunctionNameWithoutAnySpacesOrPunctuationAtAllInTheIdentifierName1234567890?",
    status: "open",
    createdAt: "2026-10-12T11:00:00Z",
  };

  return (
    <main className="min-h-screen bg-cream p-4 sm:p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          DoubtCard Test
        </h1>

        <section className="flex flex-col gap-4">
          <DoubtCard doubt={exampleOpenDoubt} />
          <DoubtCard doubt={exampleAnsweredDoubt} />
          <DoubtCard doubt={exampleLongDoubt} />
        </section>
      </div>
    </main>
  );
}
