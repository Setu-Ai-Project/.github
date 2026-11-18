import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";

import { fetchProgress } from "@/api/progressApi";
import type { ProgressSnapshot } from "@/types/progress";
import { useProgressPolling } from "./useProgressPolling";

// Created with vi.hoisted so the same (stable) function exists before vi.mock runs.
const getToken = vi.hoisted(() => vi.fn(async () => "test-token"));

vi.mock("@clerk/nextjs", () => ({ useAuth: () => ({ getToken }) }));
vi.mock("@/api/progressApi", () => ({ fetchProgress: vi.fn() }));

const mockedFetch = vi.mocked(fetchProgress);

function snapshot(totalXp: number): ProgressSnapshot {
  return { totalXp, level: 1, xpIntoLevel: totalXp, xpForNextLevel: 100, skills: [] };
}

// Moves the fake clock forward and lets the pending fetches finish.
async function advance(ms = 0) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

// Pretends the learner switched browser tabs.
async function setTabVisibility(value: DocumentVisibilityState) {
  Object.defineProperty(document, "visibilityState", { value, configurable: true });
  await act(async () => {
    document.dispatchEvent(new Event("visibilitychange"));
  });
}

beforeEach(() => {
  vi.useFakeTimers();
  mockedFetch.mockReset();
  mockedFetch.mockResolvedValue(snapshot(50));
});

afterEach(() => {
  vi.useRealTimers();
  // Remove our fake visibilityState so it can't leak into other tests.
  Reflect.deleteProperty(document, "visibilityState");
});

describe("useProgressPolling", () => {
  it("fetches straight away", async () => {
    const { result } = renderHook(() => useProgressPolling(1000));
    await advance();

    expect(mockedFetch).toHaveBeenCalledTimes(1);
    expect(mockedFetch).toHaveBeenCalledWith(getToken);
    expect(result.current.data).toEqual(snapshot(50));
    expect(result.current.loading).toBe(false);
  });

  it("fetches again every interval", async () => {
    renderHook(() => useProgressPolling(1000));
    await advance();

    await advance(1000);
    expect(mockedFetch).toHaveBeenCalledTimes(2);

    await advance(1000);
    expect(mockedFetch).toHaveBeenCalledTimes(3);
  });

  it("stops polling once the page goes away", async () => {
    const { unmount } = renderHook(() => useProgressPolling(1000));
    await advance();

    unmount();
    await advance(5000);

    expect(mockedFetch).toHaveBeenCalledTimes(1);
  });

  it("keeps the old data on screen when a later fetch fails", async () => {
    mockedFetch
      .mockResolvedValueOnce(snapshot(50))
      .mockRejectedValueOnce(new Error("boom"));
    const { result } = renderHook(() => useProgressPolling(1000));
    await advance();

    await advance(1000);

    expect(result.current.data).toEqual(snapshot(50));
    expect(result.current.error?.message).toBe("boom");
  });

  it("pauses while the tab is hidden and fetches as soon as it's back", async () => {
    renderHook(() => useProgressPolling(1000));
    await advance();

    await setTabVisibility("hidden");
    await advance(3000);
    expect(mockedFetch).toHaveBeenCalledTimes(1);

    await setTabVisibility("visible");
    await advance();
    expect(mockedFetch).toHaveBeenCalledTimes(2);
  });

  it("fetches straight away when refreshKey changes", async () => {
    const { rerender } = renderHook(
      ({ refreshKey }) => useProgressPolling(1000, refreshKey),
      { initialProps: { refreshKey: 0 } }
    );
    await advance();

    rerender({ refreshKey: 1 });
    await advance();

    expect(mockedFetch).toHaveBeenCalledTimes(2);
  });
});
