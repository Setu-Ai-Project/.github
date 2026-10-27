import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useSubmission } from "./useSubmission";
import { submitAnswer } from "@/api/submissionApi";
import type { SubmissionResult } from "@/types/submission";

vi.mock("@/api/submissionApi", () => ({ submitAnswer: vi.fn() }));
const mockSubmit = vi.mocked(submitAnswer);

const passed: SubmissionResult = {
  status: "passed",
  feedback: ["Great job!"],
  xpEarned: 50,
};
const needsRevision: SubmissionResult = {
  status: "needs_revision",
  feedback: ["First tip", "Second tip"],
  xpEarned: 0,
};

beforeEach(() => {
  mockSubmit.mockReset();
});

describe("useSubmission", () => {
  it("starts idle with no result and 0 XP", () => {
    const { result } = renderHook(() => useSubmission("c1"));
    expect(result.current.uiState).toBe("idle");
    expect(result.current.result).toBeNull();
    expect(result.current.totalXp).toBe(0);
  });

  it("is submitting with a pending result until the API resolves", async () => {
    let resolve!: (value: SubmissionResult) => void;
    mockSubmit.mockReturnValue(
      new Promise<SubmissionResult>((r) => {
        resolve = r;
      }),
    );
    const { result } = renderHook(() => useSubmission("c1"));

    let pending: Promise<void> = Promise.resolve();
    act(() => {
      pending = result.current.submit("hello");
    });
    expect(result.current.uiState).toBe("submitting");
    expect(result.current.result?.status).toBe("pending");

    await act(async () => {
      resolve(needsRevision);
      await pending;
    });
    expect(result.current.uiState).toBe("done");
  });

  it("passes the challengeId and answer to submitAnswer", async () => {
    mockSubmit.mockResolvedValue(passed);
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      await result.current.submit("correct");
    });
    expect(mockSubmit).toHaveBeenCalledWith("c1", "correct");
  });

  it("adds XP when the answer passes", async () => {
    mockSubmit.mockResolvedValue(passed);
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      await result.current.submit("correct");
    });
    expect(result.current.result?.status).toBe("passed");
    expect(result.current.totalXp).toBe(50);
  });

  it("keeps the tips and adds no XP when revision is needed", async () => {
    mockSubmit.mockResolvedValue(needsRevision);
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      await result.current.submit("hello");
    });
    expect(result.current.result?.feedback).toHaveLength(2);
    expect(result.current.totalXp).toBe(0);
  });

  it("goes to the error state when the API rejects", async () => {
    mockSubmit.mockRejectedValue(new Error("down"));
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      await result.current.submit("hello");
    });
    expect(result.current.uiState).toBe("error");
    expect(result.current.result).toBeNull();
  });

  it("retry goes back to idle and clears the result", async () => {
    mockSubmit.mockResolvedValue(needsRevision);
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      await result.current.submit("hello");
    });
    act(() => {
      result.current.retry();
    });
    expect(result.current.uiState).toBe("idle");
    expect(result.current.result).toBeNull();
  });

  it("calls the API only once when submit is called twice in the same tick", async () => {
    mockSubmit.mockResolvedValue(passed);
    const { result } = renderHook(() => useSubmission("c1"));
    await act(async () => {
      void result.current.submit("correct");
      void result.current.submit("correct");
    });
    expect(mockSubmit).toHaveBeenCalledTimes(1);
  });
});