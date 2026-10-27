import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createDoubt, listDoubts, replyToDoubt, USE_MOCK } from "./doubtApi";
import {
  mockCreateDoubt,
  mockListDoubts,
  mockReplyToDoubt,
} from "./mockDoubtApi";

vi.mock("./mockDoubtApi", () => ({
  mockListDoubts: vi.fn(),
  mockCreateDoubt: vi.fn(),
  mockReplyToDoubt: vi.fn(),
}));

describe("doubtApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("exports USE_MOCK as true by default", () => {
    expect(USE_MOCK).toBe(true);
  });

  it("listDoubts delegates to mockListDoubts and does not call fetch when USE_MOCK is true", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const fakeDoubts = [
      {
        id: "1",
        learnerName: "A",
        question: "Q",
        status: "open" as const,
        createdAt: "2026-01-01T00:00:00Z",
      },
    ];
    vi.mocked(mockListDoubts).mockResolvedValueOnce(fakeDoubts);

    const result = await listDoubts();

    expect(mockListDoubts).toHaveBeenCalledTimes(1);
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(result).toEqual(fakeDoubts);
  });

  it("createDoubt delegates to mockCreateDoubt and does not call fetch when USE_MOCK is true", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const fakeDoubt = {
      id: "2",
      learnerName: "Maya",
      question: "How do props work?",
      status: "open" as const,
      createdAt: "2026-01-01T00:00:00Z",
    };
    vi.mocked(mockCreateDoubt).mockResolvedValueOnce(fakeDoubt);

    const result = await createDoubt("How do props work?", "Maya");

    expect(mockCreateDoubt).toHaveBeenCalledWith("How do props work?", "Maya");
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(result).toEqual(fakeDoubt);
  });

  it("replyToDoubt delegates to mockReplyToDoubt and does not call fetch when USE_MOCK is true", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const fakeAnsweredDoubt = {
      id: "2",
      learnerName: "Maya",
      question: "How do props work?",
      status: "answered" as const,
      createdAt: "2026-01-01T00:00:00Z",
      reply: {
        mentorName: "Coach Alex",
        text: "Props are inputs passed into components.",
        repliedAt: "2026-01-01T01:00:00Z",
      },
    };
    vi.mocked(mockReplyToDoubt).mockResolvedValueOnce(fakeAnsweredDoubt);

    const result = await replyToDoubt(
      "2",
      "Props are inputs passed into components.",
      "Coach Alex"
    );

    expect(mockReplyToDoubt).toHaveBeenCalledWith(
      "2",
      "Props are inputs passed into components.",
      "Coach Alex"
    );
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(result).toEqual(fakeAnsweredDoubt);
  });
});
