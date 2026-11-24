import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { getMockProgress } from "@/api/mockProgress";
import SkillMap from "./SkillMap";

describe("SkillMap", () => {
  it("renders 10 mock skills across 3 tiers with 4 interactive buttons and 6 locked cards", () => {
    const { skills } = getMockProgress();
    render(<SkillMap skills={skills} />);

    expect(screen.getByRole("heading", { name: "Tier 1" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Tier 2" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Tier 3" })).toBeInTheDocument();

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(4);

    expect(screen.getByText("Swipe-Sort: AI or Not AI?")).toBeInTheDocument();
    expect(screen.getByText("AI History Timeline")).toBeInTheDocument();
    expect(screen.getByText("Case Study: DeepMind & the NHS")).toBeInTheDocument();
    expect(screen.getByText("Biased Dataset Sandbox")).toBeInTheDocument();

    const lockedIndicators = screen.getAllByText(/🔒 Locked/);
    expect(lockedIndicators).toHaveLength(6);
  });

  it("renders an empty state message when skills list is empty", () => {
    render(<SkillMap skills={[]} />);

    expect(
      screen.getByText("Your skills will appear here soon.")
    ).toBeInTheDocument();
  });
});
