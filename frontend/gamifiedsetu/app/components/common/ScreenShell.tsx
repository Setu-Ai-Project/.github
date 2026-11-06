import Link from "next/link";
import type { ReactNode } from "react";

type ScreenShellProps = {
  label: string;
  backHref?: string;
  backLabel?: string;
  children: ReactNode;
};

export default function ScreenShell({
  label,
  backHref,
  backLabel = "Back",
  children,
}: ScreenShellProps) {
  return (
    <main className="min-h-screen bg-cream px-6 py-8 text-ink">
      <div className="mx-auto w-full max-w-2xl">
        <p className="mb-6 text-sm font-bold uppercase tracking-wide text-ink/60">
          {label}
        </p>

        {backHref && (
          <Link
            href={backHref}
            className="mb-6 inline-block font-bold text-coral hover:underline"
          >
            ← {backLabel}
          </Link>
        )}

        {children}
      </div>
    </main>
  );
}