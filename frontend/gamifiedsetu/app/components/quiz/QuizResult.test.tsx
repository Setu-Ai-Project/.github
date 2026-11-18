import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import QuizResult from "./QuizResult";

function renderResult(score: number, total = 4, onRetry = () => {}) {
  render(<QuizResult score={score} total={total} moduleId="1" onRetry={onRetry} />);
}

describe("QuizResult", () => {
  it("celebrates a perfect score", () => {
    renderResult(4);

    expect(screen.getByText("You scored 4 of 4")).toBeInTheDocument();
    expect(screen.getByText("Perfect score! You really know this.")).toBeInTheDocument();
  });

  it("praises a score of at least half", () => {
    renderResult(2);
    expect(screen.getByText(/^Great work!/)).toBeInTheDocument();
  });

  it("encourages a learner who got nothing right", () => {
    renderResult(0);
    expect(screen.getByText(/^Good effort!/)).toBeInTheDocument();
  });

  it("retries and links on to the challenge", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    renderResult(2, 4, onRetry);

    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("link", { name: "Continue to challenge" })).toHaveAttribute(
      "href",
      "/challenge/1"
    );
  });
});
