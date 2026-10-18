"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

type Mode = "signup" | "login";

export default function Home() {
  const router = useRouter();

  const [mode, setMode] = useState<Mode>("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isSignup = mode === "signup";

  function toggleMode() {
    setMode(isSignup ? "login" : "signup");
    setError("");
    setPassword("");
  }

  function handleContinue(e?: React.FormEvent) {
    if (e) e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("Please enter your email address to continue.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    if (password.length < 6) {
      setError("Password should be at least 6 characters.");
      return;
    }

    setLoading(true);

    // Save demo user profile locally so the dashboard can greet them
    try {
      if (typeof window !== "undefined") {
        const username = email.split("@")[0] || "Learner";
        localStorage.setItem("setuai_user_email", email.trim());
        localStorage.setItem("setuai_user_name", username);
      }
    } catch {
      // Ignore storage errors in private mode
    }

    setTimeout(() => {
      setLoading(false);
      if (isSignup) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    }, 300);
  }

  function handleGoogleLogin() {
    setLoading(true);
    try {
      if (typeof window !== "undefined") {
        localStorage.setItem("setuai_user_email", "learner@google.com");
        localStorage.setItem("setuai_user_name", "Google Explorer");
      }
    } catch {
      // Ignore storage errors
    }

    setTimeout(() => {
      setLoading(false);
      if (isSignup) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    }, 250);
  }

  return (
    <div className="relative flex min-h-full flex-1 flex-col items-center overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6">
      {/* Background blobs */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-tealpop/40 blur-2xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-coral/25 blur-2xl"
      />

      {/* Header logo & wordmark */}
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

      {/* Auth Card matching UI/UX design specification */}
      <main className="relative z-10 mt-8 w-full max-w-md rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
        <h1 className="font-display text-[28px] font-black leading-tight">
          {isSignup ? "Create your account" : "Welcome back"}
        </h1>

        <p className="mt-1 text-[16px] text-taskgray">
          {isSignup
            ? "Join the adventure — it takes less than a minute."
            : "Pick up right where your last quest left off."}
        </p>

        {error && (
          <div
            role="alert"
            className="mt-4 rounded-xl border-2 border-coral bg-coral/10 px-4 py-3 text-[14px] font-bold text-ink"
          >
            {error}
          </div>
        )}

        <form className="mt-6 flex flex-col gap-4" onSubmit={handleContinue}>
          {/* Email */}
          <label className="flex flex-col gap-1.5 text-[16px] font-bold">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
              disabled={loading}
              className="rounded-xl border-2 border-ink/20 bg-cream px-4 py-3 font-normal outline-none placeholder:text-taskgray/70 focus:border-tealpop disabled:opacity-60"
            />
          </label>

          {/* Password */}
          <label className="flex flex-col gap-1.5 text-[16px] font-bold">
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete={isSignup ? "new-password" : "current-password"}
              required
              disabled={loading}
              className="rounded-xl border-2 border-ink/20 bg-cream px-4 py-3 font-normal outline-none placeholder:text-taskgray/70 focus:border-tealpop disabled:opacity-60"
            />
          </label>

          {/* Continue button */}
          <button
            type="submit"
            disabled={loading}
            className="mt-1 flex w-full items-center justify-center rounded-2xl border-4 border-ink bg-ink px-5 py-3 text-[16px] font-black text-cream shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Checking..." : "Continue"}
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 text-[16px] font-bold text-taskgray">
            <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
            or
            <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
          </div>

          {/* Continue with Google */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            className="flex w-full items-center justify-center gap-3 rounded-2xl border-[3px] border-ink bg-white px-5 py-3 text-[16px] font-black shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
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

        {/* Toggle Mode */}
        <p className="mt-6 text-center text-[16px]">
          {isSignup ? "Already playing? " : "New here? "}
          <button
            type="button"
            onClick={toggleMode}
            disabled={loading}
            className="font-black text-coral underline underline-offset-4 hover:opacity-80 disabled:opacity-50"
          >
            {isSignup ? "Log in" : "Sign up"}
          </button>
        </p>

        {/* Direct Dashboard Bypass Link */}
        <div className="mt-5 border-t-2 border-ink/10 pt-4 text-center">
          <Link
            href="/dashboard"
            className="font-display text-sm font-bold text-tealpop underline underline-offset-4 hover:opacity-80"
          >
            Direct Jump: Open Dashboard &rarr;
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-6 max-w-md text-center text-[16px] text-taskgray">
        Master AI through games, quizzes, and more
      </footer>
    </div>
  );
}