"use client";

import { useState } from "react";

import ErrorState from "@/app/components/common/ErrorState";
import LoadingState from "@/app/components/common/LoadingState";
import ScreenShell from "@/app/components/common/ScreenShell";

type ScreenState = "loading" | "error" | "success";

export default function ScreenStatesTestPage() {
  const [screenState, setScreenState] =
    useState<ScreenState>("loading");

  return (
    <ScreenShell
      label="Dev"
      backHref="/dashboard"
      backLabel="Back to dashboard"
    >
      <h1 className="mb-6 font-display text-3xl font-bold">
        Screen States Test
      </h1>

      <div className="mb-6 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => setScreenState("loading")}
          className="rounded-lg bg-ink px-4 py-2 font-bold text-white"
        >
          Loading
        </button>

        <button
          type="button"
          onClick={() => setScreenState("error")}
          className="rounded-lg bg-coral px-4 py-2 font-bold text-white"
        >
          Error
        </button>

        <button
          type="button"
          onClick={() => setScreenState("success")}
          className="rounded-lg bg-tealpop px-4 py-2 font-bold text-white"
        >
          Success
        </button>
      </div>

      {screenState === "loading" && <LoadingState />}

      {screenState === "error" && (
        <ErrorState
          onRetry={() => console.log("Retry clicked")}
        />
      )}

      {screenState === "success" && (
        <p className="rounded-2xl border border-ink/10 bg-white p-6 font-bold text-ink">
          Content loaded!
        </p>
      )}
    </ScreenShell>
  );
}
