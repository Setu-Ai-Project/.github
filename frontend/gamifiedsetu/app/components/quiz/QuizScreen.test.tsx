import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { checkAnswer, getQuiz } from "@/api/learningApi";
import type { AnswerCheck, Quiz } from "@/types/learning";
import QuizScreen from "./QuizScreen";

vi.mock("@/api/learningApi", () => ({ getQuiz: vi.fn(), checkAnswer: vi.fn() }));

// The mascots use next/image; a plain <img> is enough in tests.
vi.mock("next/image", () => ({
  // eslint-disable-next-line @next/next/no-img-element
  default: ({ alt, src }: { alt: string; src: string }) => <img alt={alt} src={src} />,
}));

const mockedGetQuiz = vi.mocked(getQuiz);
const mockedCheckAnswer = vi.mocked(checkAnswer);

// No correctIndex here: the screen must ask checkAnswer, never read the question.
const QUIZ: Quiz = {
  id: "quiz-1",
  moduleId: "1",
  title: "Test Quiz",
  questions: [
    { id: "q1", question: "First question?", options: ["Right one", "Wrong one"] },
    { id: "q2", question: "Second question?", options: ["Wrong two", "Right two"] },
  ],
};

// The "server" answers: question q1 → option 0, q2 → option 1.
const ANSWERS: Record<string, number> = { q1: 0, q2: 1 };

async function checkFromLookup(
  _moduleId: string,
  questionId: string,
  selectedIndex: number
): Promise<AnswerCheck> {
  return {
    correct: selectedIndex === ANSWERS[questionId],
    correctIndex: ANSWERS[questionId],
    explanation: `Because of ${questionId}.`,
  };
}

type User = ReturnType<typeof userEvent.setup>;

// Picks an option and presses "Check answer".
async function answer(user: User, option: string) {
  await user.click(await screen.findByRole("radio", { name: option }));
  await user.click(screen.getByRole("button", { name: "Check answer" }));
}

// Answers every question in order and opens the results.
async function playThrough(user: User, options: string[]) {
  for (const [i, option] of options.entries()) {
    await answer(user, option);
    const isLast = i === options.length - 1;
    await user.click(
      await screen.findByRole("button", { name: isLast ? "See results" : "Next question" })
    );
  }
}

describe("QuizScreen", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedGetQuiz.mockResolvedValue(QUIZ);
    mockedCheckAnswer.mockImplementation(checkFromLookup);
  });

  it("plays the whole quiz with all answers right", async () => {
    const user = userEvent.setup();
    render(<QuizScreen moduleId="1" />);

    expect(screen.getByText("Getting your quiz ready...")).toBeInTheDocument();
    expect(await screen.findByText("Question 1 of 2")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "← Back to lesson" })).toHaveAttribute(
      "href",
      "/learn/1"
    );

    const checkButton = screen.getByRole("button", { name: "Check answer" });
    expect(checkButton).toBeDisabled();
    await user.click(screen.getByRole("radio", { name: "Right one" }));
    expect(checkButton).toBeEnabled();

    await user.click(checkButton);
    expect(await screen.findByText("Correct!")).toBeInTheDocument();
    expect(screen.getByText("Because of q1.")).toBeInTheDocument();
    expect(screen.getByText("Nice one!")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Next question" }));
    expect(await screen.findByText("Question 2 of 2")).toBeInTheDocument();

    await answer(user, "Right two");
    await user.click(await screen.findByRole("button", { name: "See results" }));

    expect(await screen.findByText("You scored 2 of 2")).toBeInTheDocument();
    expect(screen.getByText("Perfect score! You really know this.")).toBeInTheDocument();
  });

  it("scores 0 and stays kind when every answer is wrong", async () => {
    const user = userEvent.setup();
    render(<QuizScreen moduleId="1" />);

    await answer(user, "Wrong one");
    expect(await screen.findByText("Not quite.")).toBeInTheDocument();
    expect(
      screen.getByText("Oops, close! Read the explanation and keep going.")
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Next question" }));

    await answer(user, "Wrong two");
    await user.click(await screen.findByRole("button", { name: "See results" }));

    expect(await screen.findByText("You scored 0 of 2")).toBeInTheDocument();
    expect(screen.getByText(/^Good effort!/)).toBeInTheDocument();
  });

  it("starts again from question 1 without reloading the quiz", async () => {
    const user = userEvent.setup();
    render(<QuizScreen moduleId="1" />);

    await playThrough(user, ["Right one", "Wrong two"]);
    await user.click(await screen.findByRole("button", { name: "Try again" }));

    expect(await screen.findByText("Question 1 of 2")).toBeInTheDocument();
    for (const radio of screen.getAllByRole("radio")) {
      expect(radio).not.toBeChecked();
    }
    expect(mockedGetQuiz).toHaveBeenCalledTimes(1);
  });

  it("checks only once while a check is already running", async () => {
    const user = userEvent.setup();
    // A check that never finishes, so the button stays busy.
    mockedCheckAnswer.mockReturnValue(new Promise(() => {}));
    render(<QuizScreen moduleId="1" />);

    await user.click(await screen.findByRole("radio", { name: "Right one" }));
    const checkButton = screen.getByRole("button", { name: "Check answer" });
    await user.click(checkButton);
    await user.click(checkButton);

    expect(screen.getByRole("button", { name: "Checking..." })).toBeDisabled();
    expect(mockedCheckAnswer).toHaveBeenCalledTimes(1);
  });

  it("shows a friendly message when a check fails, and lets the learner retry", async () => {
    const user = userEvent.setup();
    mockedCheckAnswer.mockRejectedValueOnce(new Error("Server down"));
    render(<QuizScreen moduleId="1" />);

    await answer(user, "Right one");
    expect(
      await screen.findByText("We could not check your answer. Please try again.")
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Check answer" }));
    expect(await screen.findByText("Correct!")).toBeInTheDocument();
  });

  it("shows the error state when the quiz fails to load, and retries", async () => {
    const user = userEvent.setup();
    mockedGetQuiz.mockRejectedValueOnce(new Error("Could not load quiz"));
    render(<QuizScreen moduleId="1" />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "We could not load this right now. Please try again."
    );

    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Question 1 of 2")).toBeInTheDocument();
    expect(mockedGetQuiz).toHaveBeenCalledTimes(2);
  });

  it("explains when the quiz has no questions", async () => {
    mockedGetQuiz.mockResolvedValue({ ...QUIZ, questions: [] });
    render(<QuizScreen moduleId="1" />);

    expect(
      await screen.findByText("This quiz has no questions yet. Check back soon!")
    ).toBeInTheDocument();
  });
});
