import Image from "next/image";
import Link from "next/link";
import { Show } from "@clerk/nextjs";

export default function Home() {
  return (
    <div className="relative flex min-h-full flex-1 flex-col items-center overflow-hidden bg-cream px-4 py-10 text-ink sm:px-6">
      {/* Background decorative blobs */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-tealpop/40 blur-2xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-coral/25 blur-2xl"
      />

      {/* Header with logo & wordmark */}
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

      {/* Main card */}
      <main className="relative z-10 mt-8 w-full max-w-md rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32] sm:p-8">
        <Show when="signed-in">
          <div className="flex flex-col items-center text-center">
            <span className="inline-block rounded-full border-2 border-ink bg-tealpop px-3 py-1 font-display text-sm font-bold text-ink">
              Signed In
            </span>
            <h1 className="mt-3 font-display text-[26px] font-black leading-tight">
              Ready to learn?
            </h1>
            <p className="mt-2 text-[16px] text-taskgray">
              Continue right where your last quest left off.
            </p>
            <Link
              href="/dashboard"
              className="mt-6 flex w-full items-center justify-center rounded-2xl border-4 border-ink bg-tealpop px-5 py-3.5 font-display text-[18px] font-black text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              Enter Dashboard &rarr;
            </Link>
            <Link
              href="/onboarding"
              className="mt-3 font-display text-sm font-bold text-coral underline underline-offset-4 hover:opacity-80"
            >
              Replay Onboarding Tour
            </Link>
          </div>
        </Show>

        <Show when="signed-out">
          <div className="flex flex-col">
            <h1 className="font-display text-[28px] font-black leading-tight">
              Start Your AI Quest
            </h1>
            <p className="mt-1 text-[16px] text-taskgray">
              Join the adventure — learn AI through mini-games, quizzes, and hands-on challenges.
            </p>

            <div className="mt-6 flex flex-col gap-3">
              {/* Sign up */}
              <Link
                href="/sign-up"
                className="flex w-full items-center justify-center rounded-2xl border-4 border-ink bg-ink px-5 py-3.5 font-display text-[16px] font-black text-cream shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
              >
                Create Account (Sign Up)
              </Link>

              {/* Log in */}
              <Link
                href="/sign-in"
                className="flex w-full items-center justify-center rounded-2xl border-4 border-ink bg-white px-5 py-3.5 font-display text-[16px] font-black text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
              >
                Log In to Existing Account
              </Link>

              {/* Divider */}
              <div className="my-1 flex items-center gap-3 text-[14px] font-bold text-taskgray">
                <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
                or
                <span aria-hidden className="h-0.5 flex-1 rounded bg-ink/10" />
              </div>

              {/* Continue with Google */}
              <Link
                href="/sign-up"
                className="flex w-full items-center justify-center gap-3 rounded-2xl border-[3px] border-ink bg-cream px-5 py-3 font-display text-[16px] font-bold text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 active:translate-y-0"
              >
                <span className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-ink bg-white text-xs font-black text-coral">
                  G
                </span>
                Continue with Google
              </Link>
            </div>

            {/* Direct preview bypass */}
            <div className="mt-6 border-t-2 border-ink/10 pt-4 text-center">
              <p className="text-xs text-taskgray">
                Testing without an account?
              </p>
              <div className="mt-2 flex justify-center gap-4 text-sm font-bold">
                <Link
                  href="/onboarding"
                  className="text-coral underline underline-offset-4 hover:opacity-80"
                >
                  Onboarding Tour
                </Link>
                <span className="text-taskgray">&bull;</span>
                <Link
                  href="/dashboard"
                  className="text-tealpop underline underline-offset-4 hover:opacity-80"
                >
                  Dashboard Preview
                </Link>
              </div>
            </div>
          </div>
        </Show>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-6 max-w-md text-center text-[16px] text-taskgray">
        Master AI through games, quizzes, and more
      </footer>
    </div>
  );
}