import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MOCK_DELAY_MS, mockSubmit } from "./mockSubmission";

describe("mockSubmit", () => {
  // Fake timers let us skip the 1.2s wait instead of really waiting.
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  async function run(answer: string) {
    const promise = mockSubmit(answer);
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    return promise;
  }

  it.each(["correct", "  CORRECT  ", "Correct"])(
    "passes %j with 50 XP",
    async (answer) => {
      const result = await run(answer);
      expect(result.status).toBe("passed");
      expect(result.xpEarned).toBe(50);
    }
  );

  it("asks for revision with 2 tips and 0 XP for any other answer", async () => {
    const result = await run("hello");
    expect(result.status).toBe("needs_revision");
    expect(result.feedback).toHaveLength(2);
    expect(result.xpEarned).toBe(0);
  });

  it("does not answer before the delay is over", async () => {
    let finished = false;
    mockSubmit("hello").then(() => {
      finished = true;
    });
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS - 1);
    expect(finished).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    expect(finished).toBe(true);
  });
});