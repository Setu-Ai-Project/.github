import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import XpBar from "./XpBar";

describe("XpBar", () => {
  it("renders progressbar with aria-valuenow 50 and text '50 / 100 XP'", () => {
    render(<XpBar current={50} max={100} />);

    const bar = screen.getByRole("progressbar", {
      name: "XP progress to the next level",
    });
    expect(bar).toHaveAttribute("aria-valuenow", "50");
    expect(screen.getByText("50 / 100 XP")).toBeInTheDocument();
  });

  it("clamps progress to 100 when current exceeds max", () => {
    render(<XpBar current={150} max={100} />);

    const bar = screen.getByRole("progressbar", {
      name: "XP progress to the next level",
    });
    expect(bar).toHaveAttribute("aria-valuenow", "100");
  });

  it("handles max 0 cleanly without NaN and displays 'Max level!'", () => {
    const { container } = render(<XpBar current={200} max={0} />);

    const bar = screen.getByRole("progressbar", {
      name: "XP progress to the next level",
    });
    expect(bar).toHaveAttribute("aria-valuenow", "100");
    expect(screen.getByText("Max level!")).toBeInTheDocument();
    expect(container.textContent).not.toContain("NaN");
  });
});
