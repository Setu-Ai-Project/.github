import { afterEach, describe, expect, it, vi } from "vitest";

import {
  checkAnswer,
  getBuilderChallenge,
  getLearnContent,
  getQuiz,
} from "./learningApi";

import {
  mockCheckAnswer,
  mockGetChallenge,
  mockGetLearnContent,
  mockGetQuiz,
} from "./mockLearning";

vi.mock("./mockLearning", () => ({
  mockGetLearnContent: vi.fn(),
  mockGetQuiz: vi.fn(),
  mockGetChallenge: vi.fn(),
  mockCheckAnswer: vi.fn(),
}));

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  vi.clearAllMocks();
});

describe("learningApi mock mode", () => {
  it("uses mock functions and never calls the network", async () => {
    vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "true");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");

    const fetchSpy = vi.spyOn(globalThis, "fetch");

    await getLearnContent("1");
    await getQuiz("1");
    await getBuilderChallenge("1");
    await checkAnswer("1", "1", 0);

    expect(mockGetLearnContent).toHaveBeenCalledWith("1");
    expect(mockGetQuiz).toHaveBeenCalledWith("1");
    expect(mockGetChallenge).toHaveBeenCalledWith("1");
    expect(mockCheckAnswer).toHaveBeenCalledWith("1", "1", 0);

    expect(fetchSpy).not.toHaveBeenCalled();
  });
});

describe("learningApi real API mode", () => {
  it("loads a quiz from the backend and converts it to frontend format", async () => {
    vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "false");
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 1,
        module_id: 1,
        title: "What Is AI? Quiz",
        questions: [
          {
            id: 1,
            question: "What is AI?",
            options: ["A", "B", "C"],
          },
        ],
      }),
    } as Response);

    const result = await getQuiz("1");

    expect(fetchSpy).toHaveBeenCalledWith(
      "http://localhost:8000/modules/1/quiz",
      undefined
    );

    expect(result).toEqual({
      id: "1",
      moduleId: "1",
      title: "What Is AI? Quiz",
      questions: [
        {
          id: "1",
          question: "What is AI?",
          options: ["A", "B", "C"],
        },
      ],
    });
  });
});

it("throws an error when the backend request fails", async () => {
  vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "false");
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");

  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: false,
  } as Response);

  await expect(getLearnContent("1")).rejects.toThrow(
    "Could not load lesson"
  );
});

it("sends an answer to the backend and converts the response", async () => {
  vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "false");
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");

  const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => ({
      correct: true,
      correct_index: 0,
      explanation: "AI enables computers to perform intelligent tasks.",
    }),
  } as Response);

  const result = await checkAnswer("1", "1", 0);

  expect(fetchSpy).toHaveBeenCalledWith(
    "http://localhost:8000/modules/1/quiz/check",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: 1,
        selected_index: 0,
      }),
    }
  );

  expect(result).toEqual({
    correct: true,
    correctIndex: 0,
    explanation: "AI enables computers to perform intelligent tasks.",
  });
});

