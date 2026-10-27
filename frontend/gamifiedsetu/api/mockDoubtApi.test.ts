import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  MOCK_DELAY_MS,
  MOCK_STORAGE_KEY,
  mockCreateDoubt,
  mockListDoubts,
  mockReplyToDoubt,
  resetMockDoubts,
} from "./mockDoubtApi";

describe("mockDoubtApi", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    resetMockDoubts();
  });

  afterEach(() => {
    resetMockDoubts();
    vi.useRealTimers();
  });

  it("1. returns an empty list initially", async () => {
    const promise = mockListDoubts();
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const doubts = await promise;
    expect(doubts).toEqual([]);
  });

  it("2. creates a doubt and lists it", async () => {
    const createPromise = mockCreateDoubt(
      "How does recursion work?",
      "Alice"
    );
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const created = await createPromise;

    expect(created.id).toBeDefined();
    expect(created.question).toBe("How does recursion work?");
    expect(created.learnerName).toBe("Alice");
    expect(created.status).toBe("open");
    expect(created.createdAt).toBeDefined();
    expect(created.reply).toBeUndefined();

    const listPromise = mockListDoubts();
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const list = await listPromise;

    expect(list).toHaveLength(1);
    expect(list[0]).toEqual(created);
  });

  it("3. generates unique IDs for two created doubts", async () => {
    const p1 = mockCreateDoubt("Doubt 1", "Learner 1");
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const d1 = await p1;

    const p2 = mockCreateDoubt("Doubt 2", "Learner 2");
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const d2 = await p2;

    expect(d1.id).not.toBe(d2.id);
  });

  it("4. replies successfully and updates the list", async () => {
    const createPromise = mockCreateDoubt(
      "What is an array?",
      "Bob"
    );
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const created = await createPromise;

    const replyPromise = mockReplyToDoubt(
      created.id,
      "An array is an ordered list of elements.",
      "Coach Dave"
    );
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const replied = await replyPromise;

    expect(replied.id).toBe(created.id);
    expect(replied.status).toBe("answered");
    expect(replied.reply).toBeDefined();
    expect(replied.reply?.mentorName).toBe("Coach Dave");
    expect(replied.reply?.text).toBe("An array is an ordered list of elements.");
    expect(replied.reply?.repliedAt).toBeDefined();

    const listPromise = mockListDoubts();
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const list = await listPromise;

    expect(list).toHaveLength(1);
    expect(list[0].status).toBe("answered");
    expect(list[0].reply?.text).toBe("An array is an ordered list of elements.");
  });

  it("5. persists doubts in localStorage under MOCK_STORAGE_KEY", async () => {
    const createPromise = mockCreateDoubt("Test persistence", "Learner");
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    const created = await createPromise;

    const raw = window.localStorage.getItem(MOCK_STORAGE_KEY);
    expect(raw).not.toBeNull();
    const parsed = JSON.parse(raw!);
    expect(Array.isArray(parsed)).toBe(true);
    expect(parsed[0].id).toBe(created.id);
  });

  it("6. rejects when replying to an unknown ID", async () => {
    const replyPromise = mockReplyToDoubt(
      "unknown-id",
      "No doubt exists",
      "Mentor"
    );
    const rejection = expect(replyPromise).rejects.toThrow("Doubt with id unknown-id not found");
    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);
    await rejection;
  });
});
