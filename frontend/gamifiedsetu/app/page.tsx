"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useSignIn, useSignUp } from "@clerk/nextjs";
import { useState } from "react";

type Mode = "signup" | "login";

export default function Home() {
  const router = useRouter();

  const {
    signIn,
    errors: signInErrors,
    fetchStatus: signInFetchStatus,
  } = useSignIn();

  const {
    signUp,
    errors: signUpErrors,
    fetchStatus: signUpFetchStatus,
  } = useSignUp();

  const [mode, setMode] = useState<Mode>("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const isSignup = mode === "signup";

  const loading =
    signInFetchStatus === "fetching" ||
    signUpFetchStatus === "fetching";

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    setError("");

    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (isSignup && password.length < 15) {
      setError("Password must be at least 15 characters.");
      return;
    }

    try {
      if (isSignup) {
        const { error: signupError } =
          await signUp.password({
            emailAddress: email.trim(),
            password,
          });

        if (signupError) {
          setError(
            signupError.message ||
              "We couldn't create your account. Please try again."
          );
          return;
        }

        /*
         * Email verification will be added later.
         *
         * If Clerk allows the signup to complete immediately,
         * finalize the session and continue to onboarding.
         */
        if (signUp.status === "complete") {
          const { error: finalizeError } =
            await signUp.finalize();

          if (finalizeError) {
            setError(
              finalizeError.message ||
                "Your account was created, but we couldn't finish signing you in."
            );
            return;
          }

          router.push("/onboarding");
          return;
        }

        setError(
          "Your account was created, but email verification is required. We'll add that next."
        );
      } else {
        const { error: signinError } =
          await signIn.password({
            emailAddress: email.trim(),
            password,
          });

        if (signinError) {
          setError(
            signinError.message ||
              "Incorrect email or password."
          );
          return;
        }

        if (signIn.status === "complete") {
          const { error: finalizeError } =
            await signIn.finalize();

          if (finalizeError) {
            setError(
              finalizeError.message ||
                "We couldn't finish signing you in."
            );
            return;
          }

          router.push("/onboarding");
          return;
        }

        setError(
          "Additional verification is required before you can sign in."
        );
      }
    } catch (err) {
      console.error("Authentication error:", err);

      // Sign-up and sign-in name the email field differently:
      // sign-up uses "emailAddress", sign-in uses "identifier".
      const emailError = isSignup
        ? signUpErrors?.fields?.emailAddress?.message
        : signInErrors?.fields?.identifier?.message;

      const passwordError = isSignup
        ? signUpErrors?.fields?.password?.message
        : signInErrors?.fields?.password?.message;

      const fieldError = emailError || passwordError;

      setError(
        fieldError ||
          "Something went wrong. Please check your details and try again."
      );
    }
  }

  function switchMode() {
    setMode(isSignup ? "login" : "signup");
    setError("");
    setPassword("");
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

      {/* Logo / wordmark */}
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

      {/* Auth card */}
      <main className="relative z-10 mt-8 w-full max-w-md rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
        <h1 className="font-display text-[28px] font-black leading-tight">
          {isSignup
            ? "Create your account"
            : "Welcome back"}
        </h1>

        <p className="mt-1 text-[16px] text-taskgray">
          {isSignup
            ? "Join the adventure — it takes less than a minute."
            : "Pick up right where your last quest left off."}
        </p>

        {/* Error */}
        {error && (
          <div
            role="alert"
            className="mt-4 rounded-xl border-2 border-coral bg-coral/10 px-4 py-3 text-[14px] font-bold text-ink"
          >
            {error}
          </div>
        )}

        <form
          className="mt-6 flex flex-col gap-4"
          onSubmit={handleSubmit}
        >
          {/* Email */}
          <label className="flex flex-col gap-1.5 text-[16px] font-bold">
            Email

            <input
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
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
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="••••••••••••••••"
              autoComplete={
                isSignup
                  ? "new-password"
                  : "current-password"
              }
              required
              minLength={15}
              disabled={loading}
              className="rounded-xl border-2 border-ink/20 bg-cream px-4 py-3 font-normal outline-none placeholder:text-taskgray/70 focus:border-tealpop disabled:opacity-60"
            />
          </label>

          {/* Clerk CAPTCHA */}
          {isSignup && (
            <div
              id="clerk-captcha"
              className="flex justify-center"
            />
          )}

          {/* Continue */}
          <button
            type="submit"
            disabled={loading}
            className="mt-1 w-full rounded-2xl border-4 border-ink bg-ink px-5 py-3 text-[16px] font-black text-cream transition-transform hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Please wait..."
              : "Continue"}
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 text-[16px] font-bold text-taskgray">
            <span
              aria-hidden
              className="h-0.5 flex-1 rounded bg-ink/10"
            />

            or

            <span
              aria-hidden
              className="h-0.5 flex-1 rounded bg-ink/10"
            />
          </div>

          {/* Google - temporarily disabled */}
          <button
            type="button"
            disabled
            className="flex w-full cursor-not-allowed items-center justify-center gap-3 rounded-2xl border-[3px] border-ink bg-white px-5 py-3 text-[16px] font-black opacity-50"
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

        {/* Switch mode */}
        <p className="mt-6 text-center text-[16px]">
          {isSignup
            ? "Already playing? "
            : "New here? "}

          <button
            type="button"
            onClick={switchMode}
            disabled={loading}
            className="font-black text-coral underline underline-offset-4 hover:opacity-80 disabled:opacity-50"
          >
            {isSignup ? "Log in" : "Sign up"}
          </button>
        </p>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-6 max-w-md text-center text-[16px] text-taskgray">
        Master AI through games, quizzes, and more
      </footer>
    </div>
  );
}