import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import ProgressBar from "./ProgressBar";

// The coloured fill is the progressbar's only child.
function fillOf(bar: HTMLElement) {
  return bar.firstElementChild as HTMLElement;
}

describe("ProgressBar", () => {
  it("exposes its label and values to screen readers", () => {
    render(<ProgressBar value={2} max={4} label="Quiz progress" />);

    const bar = screen.getByRole("progressbar", { name: "Quiz progress" });
    expect(bar).toHaveAttribute("aria-valuemin", "0");
    expect(bar).toHaveAttribute("aria-valuemax", "4");
    expect(bar).toHaveAttribute("aria-valuenow", "2");
  });

  it("fills to the matching percentage", () => {
    render(<ProgressBar value={2} max={4} label="Quiz progress" />);

    expect(fillOf(screen.getByRole("progressbar"))).toHaveStyle({ width: "50%" });
  });

  it("never fills past 100%", () => {
    render(<ProgressBar value={9} max={4} label="Quiz progress" />);

    expect(fillOf(screen.getByRole("progressbar"))).toHaveStyle({ width: "100%" });
  });

  it("shows an empty bar instead of NaN when max is 0", () => {
    render(<ProgressBar value={0} max={0} label="Quiz progress" />);

    const fill = fillOf(screen.getByRole("progressbar"));
    expect(fill).toHaveStyle({ width: "0%" });
    expect(fill.getAttribute("style")).not.toContain("NaN");
  });
});
