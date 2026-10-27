import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { submitAnswer } from "@/api/submissionApi";
import type { SubmissionResult } from "@/types/submission";
import SubmissionPanel from "./SubmissionPanel";

vi.mock("@/api/submissionApi", () => ({
  submitAnswer: vi.fn(),
}));

const mockedSubmit = vi.mocked(submitAnswer);

function answerLikeTheMock(
  _challengeId: string,
  answer: string,
): Promise<SubmissionResult> {
  if (answer.trim().toLowerCase() === "correct") {
    return Promise.resolve({
      status: "passed",
      feedback: ["Great job!"],
      xpEarned: 50,
    });
  }

  return Promise.resolve({
    status: "needs_revision",
    feedback: ["Tip one", "Tip two"],
    xpEarned: 0,
  });
}

describe("SubmissionPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedSubmit.mockImplementation(answerLikeTheMock);
  });

  it("shows feedback, keeps the answer on retry, and displays XP after passing", async () => {
    const user = userEvent.setup();

    render(<SubmissionPanel challengeId="test-challenge-1" />);

    const answerBox = screen.getByRole("textbox", {
      name: "Your answer",
    });

    await user.type(answerBox, "hello");
    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(await screen.findByText("Needs revision")).toBeInTheDocument();
    expect(screen.getByText("Tip one")).toBeInTheDocument();
    expect(screen.getByText("Tip two")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Submit" }),
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Try again" }));

    expect(answerBox).toHaveValue("hello");

    await user.clear(answerBox);
    await user.type(answerBox, "correct");
    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(await screen.findByText("Passed!")).toBeInTheDocument();
    expect(
      screen.getByText("You earned 50 XP! Total XP: 50"),
    ).toBeInTheDocument();
    expect(answerBox).toBeDisabled();
    expect(
      screen.queryByRole("button", { name: "Submit" }),
    ).not.toBeInTheDocument();
    expect(mockedSubmit).toHaveBeenCalledTimes(2);
  });

  it("disables Submit when the answer is empty or blank", async () => {
    const user = userEvent.setup();

    render(<SubmissionPanel challengeId="test-challenge-1" />);

    const submitButton = screen.getByRole("button", { name: "Submit" });
    const answerBox = screen.getByRole("textbox", {
      name: "Your answer",
    });

    expect(submitButton).toBeDisabled();

    await user.type(answerBox, "   ");

    expect(submitButton).toBeDisabled();
  });

  it("shows a friendly error and allows another attempt", async () => {
    const user = userEvent.setup();

    mockedSubmit.mockRejectedValueOnce(new Error("Network error"));

    render(<SubmissionPanel challengeId="test-challenge-1" />);

    await user.type(
      screen.getByRole("textbox", { name: "Your answer" }),
      "correct",
    );

    await user.click(screen.getByRole("button", { name: "Submit" }));

    expect(
      await screen.findByText(
        "We could not check your answer. Please try again in a moment.",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: "Submit" }),
    ).toBeEnabled();
  });

  it("announces submission results through a polite live region", () => {
    const { container } = render(
      <SubmissionPanel challengeId="test-challenge-1" />,
    );

    expect(container.querySelector('[aria-live="polite"]')).toBeInTheDocument();
  });
});