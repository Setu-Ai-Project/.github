import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  MOCK_DELAY_MS,
  MOCK_CHECK_DELAY_MS,
  mockCheckAnswer,
  mockGetChallenge,
  mockGetLearnContent,
  mockGetQuiz,
} from "./mockLearning";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("mockGetLearnContent", () => {
  it("loads lesson content for module 1", async () => {
    const promise = mockGetLearnContent("1");

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

    const result = await promise;

    expect(result.id).toBe("1");
    expect(result.moduleId).toBe("1");
    expect(result.title).toBe("What Is AI?");
    expect(result.sections).toHaveLength(4);
  });
});

describe("mockGetQuiz", () => {
  it("loads quiz questions for module 1", async () => {
    const promise = mockGetQuiz("1");

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

    const result = await promise;

    expect(result.id).toBe("1");
    expect(result.moduleId).toBe("1");
    expect(result.title).toBe("What Is AI? Quiz");
    expect(result.questions).toHaveLength(4);
  });
});

describe("mockGetChallenge", () => {
  it("loads the Builder Challenge for module 1", async () => {
    const promise = mockGetChallenge("1");

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

    const result = await promise;

    expect(result.id).toBe("1");
    expect(result.moduleId).toBe("1");
    expect(result.title).toBe("Describe a sunset");
    expect(result.hints).toHaveLength(2);
  });
});

describe("unknown modules", () => {
  it("throws an error when the lesson module does not exist", async () => {
    const promise = mockGetLearnContent("99");

    const rejection = expect(promise).rejects.toThrow("Module not found");

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

    await rejection;
  });
  it("throws an error when the quiz module does not exist", async () => {
  const promise = mockGetQuiz("99");

  const rejection = expect(promise).rejects.toThrow("Module not found");

  await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

  await rejection;
});

it("throws an error when the challenge module does not exist", async () => {
  const promise = mockGetChallenge("99");

  const rejection = expect(promise).rejects.toThrow("Module not found");

  await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS);

  await rejection;
});
});

describe("mock network delay", () => {
  it("waits for the configured delay before returning lesson content", async () => {
    let resolved = false;

    const promise = mockGetLearnContent("1").then((result) => {
      resolved = true;
      return result;
    });

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS - 1);

    expect(resolved).toBe(false);

    await vi.advanceTimersByTimeAsync(1);

    const result = await promise;

    expect(resolved).toBe(true);
    expect(result.title).toBe("What Is AI?");
  });
});

describe("mockCheckAnswer", () => {
  it("returns correct when the learner selects the right answer", async () => {
    const promise = mockCheckAnswer("1", "1", 0);

    await vi.advanceTimersByTimeAsync(MOCK_CHECK_DELAY_MS);

    const result = await promise;

    expect(result.correct).toBe(true);
    expect(result.correctIndex).toBe(0);
    expect(result.explanation).toBeDefined();
  });
  it("returns incorrect when the learner selects the wrong answer", async () => {
  const promise = mockCheckAnswer("1", "1", 1);

  await vi.advanceTimersByTimeAsync(MOCK_CHECK_DELAY_MS);

  const result = await promise;

  expect(result.correct).toBe(false);
  expect(result.correctIndex).toBe(0);
  expect(result.explanation).toBeDefined();
});
it("throws an error when the question does not exist", async () => {
  const promise = mockCheckAnswer("1", "99", 0);

  const rejection = expect(promise).rejects.toThrow("Question not found");

  await vi.advanceTimersByTimeAsync(MOCK_CHECK_DELAY_MS);

  await rejection;
});
});



