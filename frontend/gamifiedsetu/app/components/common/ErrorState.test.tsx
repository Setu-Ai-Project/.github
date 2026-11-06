import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import ErrorState from "./ErrorState";

describe("ErrorState", () => {
  it("displays the default error message", () => {
    render(<ErrorState onRetry={() => {}} />);

    expect(
      screen.getByText(
        "We could not load this right now. Please try again."
      )
    ).toBeInTheDocument();
  });

  it("displays a custom error message", () => {
    render(
      <ErrorState
        message="Could not load your lesson."
        onRetry={() => {}}
      />
    );

    expect(
      screen.getByText("Could not load your lesson.")
    ).toBeInTheDocument();
  });

  it("calls onRetry when the button is clicked", () => {
    const onRetry = vi.fn();

    render(<ErrorState onRetry={onRetry} />);

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});