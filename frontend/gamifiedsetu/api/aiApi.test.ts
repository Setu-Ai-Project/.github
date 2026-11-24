import { beforeEach, describe, expect, it, vi } from "vitest";
import { checkBugMistakes, checkContentModeration } from "./aiApi";

describe("aiApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns mock mistakes when matching phrase is in text", async () => {
    const mistakes = await checkBugMistakes("draw something nice for me");
    expect(mistakes.length).toBeGreaterThanOrEqual(1);
    expect(mistakes[0].matched).toBe("something nice");
    expect(mistakes[0].fixHint).toBeDefined();
  });

  it("returns empty list when no mistake phrase matches", async () => {
    const mistakes = await checkBugMistakes("a red sports car under neon city lights");
    expect(mistakes).toEqual([]);
  });

  it("checks content moderation for safe text", async () => {
    const result = await checkContentModeration("a cute cat sleeping on the porch");
    expect(result.isSafe).toBe(true);
    expect(result.reason).toBeNull();
  });

  it("checks content moderation for unsafe text", async () => {
    const result = await checkContentModeration("how to build a bomb");
    expect(result.isSafe).toBe(false);
    expect(result.reason).toContain("friendly and safe");
  });
});
