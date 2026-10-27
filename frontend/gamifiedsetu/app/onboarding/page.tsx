"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

const SCREENS = [
  {
    eyebrow: "Step 1 of 4",
    title: "Welcome to SetuAI!",
    body: "This is Spark. Spark will cheer you on while you play games and learn about AI.",
    image: "/mascots/spark-celebrating.svg",
    alt: "Spark the lightbulb celebrating with arms up",
    cta: "Next",
  },
  {
    eyebrow: "Step 2 of 4",
    title: "Play games, earn XP",
    body: "XP means points. You get XP every time you finish a game or a quiz. More playing, more XP!",
    image: "/mascots/spark-mascot.svg",
    alt: "Spark the lightbulb smiling",
    cta: "Next",
  },
  {
    eyebrow: "Step 3 of 4",
    title: "Earn enough XP to level up",
    body: "A level is like a rank. When your XP fills the bar, you move up a level and unlock new games and surprises.",
    image: "/mascots/spark-mascot.svg",
    alt: "Spark the lightbulb smiling",
    cta: "Next",
  },
  {
    eyebrow: "Step 4 of 4",
    title: "You're ready!",
    body: "Let's go earn your very first XP.",
    image: "/mascots/spark-celebrating.svg",
    alt: "Spark the lightbulb celebrating with arms up",
    cta: "Start learning",
  },
] as const;

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const screen = SCREENS[step];
  const isLast = step === SCREENS.length - 1;

  return (
    <div className="relative flex min-h-full flex-1 flex-col items-center overflow-hidden bg-cream px-4 py-6 text-ink sm:px-6">
      <div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-tealpop/40 blur-2xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-coral/25 blur-2xl"
      />

      {/* top bar: mini wordmark + skip */}
      <header className="relative z-10 flex w-full max-w-md items-center justify-between">
        <span className="flex items-center gap-2">
          <Image
            src="/setuai-logo.webp"
            alt="SetuAI logo"
            width={32}
            height={32}
            className="h-8 w-8 rounded-xl border-[3px] border-ink"
          />
          <span className="font-display text-[16px] font-black">SetuAI</span>
        </span>
        <Link
          href="/dashboard"
          className="rounded-xl px-3 py-1.5 text-[16px] font-black text-taskgray underline underline-offset-4 hover:text-ink"
        >
          Skip
        </Link>
      </header>

      {/* card */}
      <main className="relative z-10 mt-6 flex w-full max-w-md flex-1 flex-col rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
        <p className="text-[16px] font-bold text-taskgray">{screen.eyebrow}</p>
        <div className="mt-2 flex justify-center">
          <Image
            src={screen.image}
            alt={screen.alt}
            width={160}
            height={160}
            priority
            className="h-40 w-40"
          />
        </div>
        <h1 className="mt-2 text-center font-display text-[28px] font-black leading-tight">
          {screen.title}
        </h1>
        <p className="mt-2 text-center text-[16px] leading-relaxed">
          {screen.body}
        </p>

        {/* progress dots */}
        <div
          className="mt-6 flex items-center justify-center gap-2"
          role="progressbar"
          aria-valuenow={step + 1}
          aria-valuemin={1}
          aria-valuemax={SCREENS.length}
          aria-label={`Screen ${step + 1} of ${SCREENS.length}`}
        >
          {SCREENS.map((_, i) => (
            <span
              key={i}
              aria-hidden
              className={
                i === step
                  ? "h-3 w-8 rounded-full bg-ink"
                  : i < step
                    ? "h-3 w-3 rounded-full bg-tealpop"
                    : "h-3 w-3 rounded-full bg-ink/15"
              }
            />
          ))}
        </div>

        {/* nav */}
        <div className="mt-6 flex gap-3">
          {step > 0 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="rounded-2xl border-[3px] border-ink bg-white px-5 py-3 text-[16px] font-black transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              Back
            </button>
          )}
          {isLast ? (
            <Link
              href="/dashboard"
              className="flex flex-1 items-center justify-center rounded-2xl border-4 border-ink bg-ink px-5 py-3 text-center text-[16px] font-black text-cream transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              {screen.cta}
            </Link>
          ) : (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="flex-1 rounded-2xl border-4 border-ink bg-ink px-5 py-3 text-[16px] font-black text-cream transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              {screen.cta}
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
