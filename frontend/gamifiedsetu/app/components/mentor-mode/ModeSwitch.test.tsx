import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ModeProvider, useMode } from "@/context/ModeContext";
import ModeSwitch from "./ModeSwitch";

// Prints the current mode so the test can check the switch really changed it.
function ShowMode() {
  const { mode } = useMode();
  return <p>Current mode: {mode}</p>;
}

function renderSwitch() {
  render(
    <ModeProvider>
      <ModeSwitch />
      <ShowMode />
    </ModeProvider>
  );
}

describe("ModeSwitch", () => {
  it("shows Learner as pressed by default", () => {
    renderSwitch();
    expect(screen.getByRole("button", { name: "Learner" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Mentor" })).toHaveAttribute("aria-pressed", "false");
  });

  it("switches to mentor and back when clicked", async () => {
    const user = userEvent.setup();
    renderSwitch();

    await user.click(screen.getByRole("button", { name: "Mentor" }));
    expect(screen.getByText("Current mode: mentor")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mentor" })).toHaveAttribute("aria-pressed", "true");

    await user.click(screen.getByRole("button", { name: "Learner" }));
    expect(screen.getByText("Current mode: learner")).toBeInTheDocument();
  });

  it("is labelled as a group for screen readers", () => {
    renderSwitch();
    expect(screen.getByRole("group", { name: "Switch mode" })).toBeInTheDocument();
  });
});
