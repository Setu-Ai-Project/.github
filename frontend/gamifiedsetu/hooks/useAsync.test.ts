import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useAsync } from "./useAsync";

describe("useAsync", () => {
  it("starts in the loading state", () => {
    const asyncFunction = vi.fn(
      () => new Promise<string>(() => {})
    );

    const { result } = renderHook(() => useAsync(asyncFunction));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
  });

  it("stores data when the request succeeds", async () => {
    const asyncFunction = vi.fn().mockResolvedValue("Lesson data");

    const { result } = renderHook(() => useAsync(asyncFunction));

    await waitFor(() => {
      expect(result.current.data).toBe("Lesson data");
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("stores an error when the request fails", async () => {
    const asyncFunction = vi
      .fn()
      .mockRejectedValue(new Error("Could not load lesson"));

    const { result } = renderHook(() => useAsync(asyncFunction));

    await waitFor(() => {
      expect(result.current.error?.message).toBe("Could not load lesson");
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe(null);
  });

  it("reloads data when reload is called", async () => {
    const asyncFunction = vi
      .fn()
      .mockResolvedValueOnce("First result")
      .mockResolvedValueOnce("Second result");

    const { result } = renderHook(() => useAsync(asyncFunction));

    await waitFor(() => {
      expect(result.current.data).toBe("First result");
    });

    act(() => {
      result.current.reload();
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.data).toBe("Second result");
    });

    expect(asyncFunction).toHaveBeenCalledTimes(2);
  });
  it("does not load again on a normal re-render (no infinite loop)", async () => {
  const asyncFunction = vi.fn().mockResolvedValue("hi");

  const { result, rerender } = renderHook(() => useAsync(asyncFunction));

  await waitFor(() => expect(result.current.loading).toBe(false));

  rerender();

  expect(asyncFunction).toHaveBeenCalledTimes(1);
});
});