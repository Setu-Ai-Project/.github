import Image from "next/image";
import Link from "next/link";

export default function Dashboard() {
  return (
    <div className="relative flex min-h-full flex-1 flex-col items-center bg-cream px-4 py-10 text-ink sm:px-6">
      <header className="flex items-center gap-3">
        <Image
          src="/setuai-logo.webp"
          alt="SetuAI logo"
          width={48}
          height={48}
          className="h-12 w-12 rounded-2xl border-4 border-ink shadow-[4px_4px_0_#172A32]"
        />
        <span className="font-display text-[28px] font-black tracking-tight">
          SetuAI
        </span>
      </header>

      <main className="mt-8 w-full max-w-md rounded-3xl border-4 border-ink bg-white p-6 text-center shadow-[8px_8px_0_#172A32] sm:p-8">
        <h1 className="font-display text-[28px] font-black">
          Your dashboard is coming soon
        </h1>
        <p className="mt-2 text-[16px] text-taskgray">
          You finished onboarding with 0 XP. Play your first game to earn some!
        </p>
        <div className="mt-6 rounded-2xl border-[3px] border-ink bg-cream p-4">
          <p className="text-[16px] font-black">Level 1 · 0 XP</p>
          <div
            className="mt-2 h-4 overflow-hidden rounded-full border-2 border-ink bg-white"
            role="progressbar"
            aria-valuenow={0}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="XP progress"
          >
            <div className="h-full w-0 rounded-full bg-tealpop" />
          </div>
        </div>
        <Link
          href="/onboarding"
          className="mt-6 inline-block font-black text-coral underline underline-offset-4 hover:opacity-80"
        >
          Replay the tour
        </Link>
      </main>
    </div>
  );
}
