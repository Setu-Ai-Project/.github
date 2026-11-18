"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

import { fetchProgress } from "@/api/progressApi";
import type { ProgressSnapshot } from "@/types/progress";

// How often to ask for fresh progress. Set NEXT_PUBLIC_POLL_INTERVAL_MS to change it.
export const DEFAULT_POLL_MS = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS) || 5000;

// Fetches progress now, then every `intervalMs`, but only while the tab is visible.
// Changing `refreshKey` fetches again straight away ("Try again" and Task 20's
// WebSocket use this).
export function useProgressPolling(intervalMs: number = DEFAULT_POLL_MS, refreshKey = 0) {
  // getToken is stable (Clerk wraps it in useCallback), so it is safe in the deps below.
  const { getToken } = useAuth();
  const [data, setData] = useState<ProgressSnapshot | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Becomes true when the page goes away, so late answers are ignored.
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | undefined;

    async function load() {
      try {
        // fetchProgress only asks for the login token in real mode.
        const snapshot = await fetchProgress(getToken);
        if (cancelled) return;
        setData(snapshot);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        // Keep the old data on screen; just remember the error.
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    function start() {
      void load(); // fetch now...
      timer = setInterval(() => void load(), intervalMs); // ...then again every intervalMs
    }

    function stop() {
      if (timer) clearInterval(timer);
      timer = undefined;
    }

    // Pause while the tab is hidden; fetch straight away when it comes back.
    function onVisibilityChange() {
      if (document.visibilityState === "hidden") stop();
      else if (!timer) start();
    }

    if (document.visibilityState !== "hidden") start();
    document.addEventListener("visibilitychange", onVisibilityChange);

    // CLEANUP: stop the timer and the listener when the page goes away.
    // Forgetting this keeps polling forever in the background.
    return () => {
      cancelled = true;
      stop();
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [intervalMs, refreshKey, getToken]);

  return { data, error, loading };
}
