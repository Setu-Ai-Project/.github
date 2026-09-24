"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";

type Mode = "signup" | "login";

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("signup");
  const isSignup = mode === "signup";

  return (
    <div className="relative flex min-h-full flex-1 flex-col items-center overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6">
      {/* playful background blobs */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-tealpop/40 blur-2xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-coral/25 blur-2xl"
      />

      {/* logo / wordmark */}
      <header className="relative z-10 flex flex-col items-center gap-3 text-center">
        <div className="flex items-center gap-3">
          <Image
            src="/setuai-logo.webp"
            alt="SetuAI logo"
            width={48}
            height={48}
            priority
            className="h-12 w-12 rounded-2xl border-4 border-ink shadow-[4px_4px_0_#172A32]"
          />
          <span className="font-display text-[28px] font-black tracking-tight">
            SetuAI
          </span>
        </div>
        <p className="font-display-italic text-[24px] italic opacity-80">
          The Next Step in AI Literacy
        </p>
      </header>

      {/* auth card */}
      <main className="relative z-10 mt-8 w-full max-w-md rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
        <h1 className="font-display text-[28px] font-black leading-tight">
          {isSignup ? "Create your account" : "Welcome back"}
        </h1>
        <p className="mt-1 text-[16px] text-taskgray">
          {isSignup
            ? "Join the adventure — it takes less than a minute."
            : "Pick up right where your last quest left off."}
        </p>

        <form
          className="mt-6 flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            router.push("/onboarding");
          }}
        >
          <label className="flex flex-col gap-1.5 text-[16px] font-bold">
            Email
            <input
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              className="rounded-xl border-2 border-ink/20 bg-cream px-4 py-3 font-normal outline-none placeholder:text-taskgray/70 focus:border-tealpop"
            />
          </label>

          <label className="flex flex-col gap-1.5 text-[16px] font-bold">
            Password
            <input
              type="password"
              placeholder="••••••••"
              autoComplete={isSignup ? "new-password" : "current-password"}
              className="rounded-xl border-2 border-ink/20 bg-cream px-4 py-3 font-normal outline-none placeholder:text-taskgray/70 focus:border-tealpop"
            />
          </label>

          <button
            type="submit"
            className="mt-1 w-full rounded-2xl border-4 border-ink bg-ink px-5 py-3 text-[16px] font-black text-cream transition-transform hover:-translate-y-0.5 active:translate-y-0"
          >
            Continue
          </button>

          <div className="flex items-center gap-3 text-[16px] font-bold text-taskgray">
            <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
            or
            <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
          </div>

          <button
            type="button"
            className="flex w-full items-center justify-center gap-3 rounded-2xl border-[3px] border-ink bg-white px-5 py-3 text-[16px] font-black transition-transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <span
              aria-hidden
              className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-ink bg-cream text-sm font-black text-coral"
            >
              G
            </span>
            Continue with Google
          </button>
        </form>

        <p className="mt-6 text-center text-[16px]">
          {isSignup ? "Already playing? " : "New here? "}
          <button
            type="button"
            onClick={() => setMode(isSignup ? "login" : "signup")}
            className="font-black text-coral underline underline-offset-4 hover:opacity-80"
          >
            {isSignup ? "Log in" : "Sign up"}
          </button>
        </p>
      </main>

      <footer className="relative z-10 mt-6 max-w-md text-center text-[16px] text-taskgray">
        Master AI through games, quizzes, and more
      </footer>
    </div>
  );
}
