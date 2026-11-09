
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import HintList from "./HintList";

describe("HintList", () => {
  it("shows a message when there are no hints", () => {
    render(<HintList hints={[]} />);

    expect(
      screen.getByText("No hints for this challenge.")
    ).toBeInTheDocument();

    expect(
      screen.queryByRole("button")
    ).not.toBeInTheDocument();
  });

  it("reveals one hint at a time", () => {
    render(
      <HintList
        hints={["Start with a simple idea.", "Test your solution."]}
      />
    );

    expect(screen.getByText("0 of 2 hints shown")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Show next hint" }));

    expect(screen.getByText("Start with a simple idea.")).toBeInTheDocument();
    expect(screen.getByText("1 of 2 hints shown")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Show next hint" }));

    expect(screen.getByText("Test your solution.")).toBeInTheDocument();
    expect(screen.getByText("2 of 2 hints shown")).toBeInTheDocument();
  });

  it("disables the button when all hints are shown", () => {
    render(<HintList hints={["First hint"]} />);

    fireEvent.click(screen.getByRole("button", { name: "Show next hint" }));

    expect(
      screen.getByRole("button", { name: "No more hints" })
    ).toBeDisabled();
  });

  it("calls onReveal with the number of hints shown", () => {
    const onReveal = vi.fn();

    render(
      <HintList
        hints={["First hint", "Second hint"]}
        onReveal={onReveal}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Show next hint" }));

    expect(onReveal).toHaveBeenCalledWith(1);
  });
});
