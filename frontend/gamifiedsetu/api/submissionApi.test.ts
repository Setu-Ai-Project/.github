import { describe, expect, it, vi } from "vitest";
import { submitAnswer } from "./submissionApi";
import { mockSubmit } from "./mockSubmission";

// Replace the real mock with an instant fake so we can check it was called.
vi.mock("./mockSubmission", () => ({
  mockSubmit: vi.fn(async () => ({
    status: "passed",
    feedback: [],
    xpEarned: 50,
  })),
}));

describe("submitAnswer", () => {
  it("uses the mock and never calls the network while USE_MOCK is true", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");

    const result = await submitAnswer("challenge-1", "hello");

    expect(mockSubmit).toHaveBeenCalledWith("hello");
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(result.status).toBe("passed");
  });
});