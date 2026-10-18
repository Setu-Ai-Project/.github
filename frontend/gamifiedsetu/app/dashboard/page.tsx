"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

const LEVELS = [
  {
    id: 1,
    title: "Level 1: What Is AI?",
    category: "Foundation",
    description: "Sort real-world examples into AI, Not AI, and AGI hype myths across interactive swipe rounds.",
    status: "Completed",
    xp: 50,
    badge: "AI Explorer",
    iconColor: "bg-tealpop",
    route: "/dev/submission",
  },
  {
    id: 2,
    title: "Level 2: Prompt Engineering",
    category: "Prompt Lab",
    description: "Hunt down AI hallucinations and tweak descriptive prompts to recreate reference images in the Prompt Lab.",
    status: "Current Quest",
    xp: 50,
    badge: "Prompt Architect",
    iconColor: "bg-coral",
    route: "/dev/submission",
  },
  {
    id: 3,
    title: "Level 3: AI Literacy for Students",
    category: "Decision Scenarios",
    description: "Pick the best AI tools for realistic student assignments and analyze outcomes.",
    status: "Unlocked",
    xp: 50,
    badge: "Ethical Builder",
    iconColor: "bg-cream",
    route: "/dev/learner-doubts-test",
  },
  {
    id: 4,
    title: "Level 4: Talking to Machines",
    category: "Mock Terminal",
    description: "Type real simulated terminal commands and explore developer workflows safely.",
    status: "Locked",
    xp: 50,
    badge: "Terminal Hacker",
    iconColor: "bg-white",
    route: "#",
  },
  {
    id: 5,
    title: "Level 5: Creative Expression & AI",
    category: "Deepfake Quiz",
    description: "Spot the fakes in 8–10 image pairs and remix your own creations side-by-side with AI.",
    status: "Locked",
    xp: 50,
    badge: "Remix Master",
    iconColor: "bg-white",
    route: "#",
  },
  {
    id: 6,
    title: "Level 6: AI Entrepreneurship",
    category: "Flagship Level",
    description: "Build an MVP chatbot and drag-and-fill your 12-box Lean Canvas startup business plan.",
    status: "Flagship",
    xp: 100,
    badge: "AI Founder",
    iconColor: "bg-white",
    route: "#",
  },
  {
    id: 7,
    title: "Level 7: Future Implications & Ethics",
    category: "Final Certificate",
    description: "Complete the AI Readiness scorecard and download your personalized curriculum completion certificate.",
    status: "Locked",
    xp: 100,
    badge: "Graduate",
    iconColor: "bg-white",
    route: "#",
  },
];

export default function Dashboard() {
  const [userName, setUserName] = useState("Learner");
  const [userXp] = useState(50);
  const totalXpRequired = 100;
  const progressPercent = Math.min(100, Math.round((userXp / totalXpRequired) * 100));

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedName = localStorage.getItem("setuai_user_name");
      if (storedName) setUserName(storedName);
    }
  }, []);

  return (
    <div className="relative flex min-h-screen flex-col bg-cream text-ink">
      {/* Top Navbar */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b-4 border-ink bg-white px-4 py-3 sm:px-8">
        <div className="flex items-center gap-3">
          <Image
            src="/setuai-logo.webp"
            alt="SetuAI logo"
            width={40}
            height={40}
            className="h-10 w-10 rounded-xl border-[3px] border-ink shadow-[2px_2px_0_#172A32]"
          />
          <div>
            <span className="font-display text-[22px] font-black tracking-tight">
              SetuAI
            </span>
            <span className="ml-2 hidden rounded-full border-2 border-ink bg-tealpop px-2.5 py-0.5 font-display text-xs font-bold sm:inline-block">
              Curriculum Map
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/dev/learner-doubts-test"
            className="hidden items-center gap-1.5 rounded-xl border-2 border-ink bg-cream px-3 py-1.5 font-display text-sm font-bold shadow-[2px_2px_0_#172A32] transition-transform hover:-translate-y-0.5 sm:flex"
          >
            Ask a Mentor
          </Link>
          <div className="flex items-center gap-2 rounded-xl border-2 border-ink bg-cream px-3 py-1 font-display text-sm font-black">
            <span className="text-coral">★</span>
            <span>{userXp} XP</span>
          </div>
          <Link
            href="/"
            className="rounded-xl border-2 border-ink bg-white px-3 py-1 font-display text-sm font-bold hover:bg-cream"
          >
            Sign Out
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6">
        {/* Welcome & Progress Overview */}
        <section className="rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display text-sm font-black uppercase tracking-wider text-coral">
                  Active Learner
                </span>
                <span className="h-1.5 w-1.5 rounded-full bg-ink/30" />
                <span className="text-sm font-bold text-taskgray">Day 1 Streak 🔥</span>
              </div>
              <h1 className="mt-1 font-display text-3xl font-black sm:text-4xl">
                Welcome back, {userName}!
              </h1>
              <p className="mt-2 text-base text-taskgray sm:text-lg">
                You have finished onboarding and completed Level 1. Level 2 (Prompt Lab) is ready for you!
              </p>
            </div>

            {/* Level status card */}
            <div className="min-w-[260px] rounded-2xl border-4 border-ink bg-cream p-5 shadow-[4px_4px_0_#172A32]">
              <div className="flex items-center justify-between font-display font-black">
                <span className="text-lg">Level 1: Novice</span>
                <span className="rounded-full border-2 border-ink bg-tealpop px-2.5 py-0.5 text-xs">
                  {userXp} / {totalXpRequired} XP
                </span>
              </div>
              <div
                className="mt-3 h-4 w-full overflow-hidden rounded-full border-2 border-ink bg-white"
                role="progressbar"
                aria-valuenow={progressPercent}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="h-full rounded-full bg-tealpop transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <p className="mt-2 text-xs font-bold text-taskgray">
                Earn 50 more XP to unlock Level 2 and the Ethical Builder Badge!
              </p>
            </div>
          </div>
        </section>

        {/* Mascot Quest Spotlight */}
        <section className="flex flex-col items-center gap-4 rounded-3xl border-4 border-ink bg-coral/10 p-6 shadow-[6px_6px_0_#172A32] sm:flex-row sm:items-center sm:justify-between sm:p-6">
          <div className="flex items-center gap-4">
            <Image
              src="/mascots/nova-mascot.svg"
              alt="Nova Mascot"
              width={64}
              height={64}
              className="h-16 w-16"
            />
            <div>
              <span className="font-display text-xs font-black uppercase text-coral">
                Nova&apos;s Active Quest
              </span>
              <h2 className="font-display text-xl font-black">
                Challenge Lab: Recreate the AI Image
              </h2>
              <p className="text-sm text-taskgray">
                Type your answer into the prompt verification sandbox and earn 50 instant XP.
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Link
              href="/dev/submission"
              className="flex items-center rounded-2xl border-4 border-ink bg-coral px-5 py-3 font-display text-sm font-black text-white shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              Play Challenge Lab &rarr;
            </Link>
          </div>
        </section>

        {/* 7-Level Curriculum Grid */}
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-2xl font-black">
              Curriculum Modules &amp; Quests
            </h2>
            <span className="text-sm font-bold text-taskgray">
              7 Total Levels
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {LEVELS.map((lvl) => {
              const isLocked = lvl.status === "Locked";
              const isCurrent = lvl.status === "Current Quest";

              return (
                <div
                  key={lvl.id}
                  className={`flex flex-col justify-between rounded-2xl border-4 border-ink p-5 shadow-[4px_4px_0_#172A32] transition-transform ${
                    isCurrent
                      ? "bg-white ring-4 ring-coral/40"
                      : isLocked
                      ? "bg-cream/60 opacity-75"
                      : "bg-white"
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="rounded-md border border-ink bg-cream px-2 py-0.5 font-display text-xs font-bold text-ink">
                        {lvl.category}
                      </span>
                      <span
                        className={`rounded-full border-2 border-ink px-2.5 py-0.5 font-display text-xs font-bold ${
                          lvl.status === "Completed"
                            ? "bg-tealpop text-ink"
                            : lvl.status === "Current Quest"
                            ? "bg-coral text-white"
                            : lvl.status === "Flagship"
                            ? "bg-amber-300 text-ink"
                            : "bg-taskgray/20 text-taskgray"
                        }`}
                      >
                        {lvl.status}
                      </span>
                    </div>

                    <h3 className="mt-3 font-display text-xl font-black">
                      {lvl.title}
                    </h3>

                    <p className="mt-1.5 text-sm text-taskgray">
                      {lvl.description}
                    </p>
                  </div>

                  <div className="mt-5 flex items-center justify-between border-t border-ink/10 pt-4">
                    <div className="flex items-center gap-1 font-display text-xs font-bold text-taskgray">
                      <span>Reward:</span>
                      <span className="font-black text-coral">+{lvl.xp} XP</span>
                      <span>· {lvl.badge}</span>
                    </div>

                    {isLocked ? (
                      <span className="cursor-not-allowed font-display text-xs font-bold text-taskgray">
                        Locked
                      </span>
                    ) : (
                      <Link
                        href={lvl.route}
                        className="rounded-xl border-2 border-ink bg-tealpop px-3 py-1.5 font-display text-xs font-black shadow-[2px_2px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
                      >
                        {lvl.status === "Completed" ? "Replay" : "Enter Level &rarr;"}
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Quick Utilities Footer Bar */}
        <section className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border-4 border-ink bg-white p-5 shadow-[4px_4px_0_#172A32]">
          <div>
            <h3 className="font-display text-base font-black">
              Need Help with a Concept?
            </h3>
            <p className="text-xs text-taskgray">
              Post questions to mentors or chat with Bug, Spark, and Byte.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/dev/learner-doubts-test"
              className="rounded-xl border-2 border-ink bg-cream px-4 py-2 font-display text-xs font-black shadow-[2px_2px_0_#172A32] hover:bg-tealpop"
            >
              Ask a Doubt
            </Link>
            <Link
              href="/onboarding"
              className="rounded-xl border-2 border-ink bg-white px-4 py-2 font-display text-xs font-bold hover:bg-cream"
            >
              Replay Onboarding
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
