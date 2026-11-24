import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { Skill } from "@/types/progress";
import SkillNode from "./SkillNode";

const baseSkill: Skill = {
  id: "s1",
  name: "Swipe-Sort: AI or Not AI?",
  description: "Sort everyday gadgets into AI and not AI.",
  moduleId: "1",
  status: "complete",
  prerequisites: [],
  xpReward: 50,
  progress: 100,
};

describe("SkillNode", () => {
  it("renders a complete skill as a button with '+50 XP' and appropriate accessible name", () => {
    render(<SkillNode skill={baseSkill} />);

    const button = screen.getByRole("button", {
      name: "Skill: Swipe-Sort: AI or Not AI?, Complete",
    });
    expect(button).toBeInTheDocument();
    expect(screen.getByText("+50 XP")).toBeInTheDocument();
    expect(screen.getByText("✓ Complete")).toBeInTheDocument();
  });

  it("renders an in-progress skill with progress bar percentage and accessible name", () => {
    const inProgressSkill: Skill = {
      ...baseSkill,
      id: "s2",
      name: "AI History Timeline",
      status: "in-progress",
      progress: 40,
    };

    render(<SkillNode skill={inProgressSkill} />);

    const button = screen.getByRole("button", {
      name: "Skill: AI History Timeline, In progress",
    });
    expect(button).toBeInTheDocument();
    expect(screen.getByText("40% done")).toBeInTheDocument();
  });

  it("renders a locked skill as a non-button element with prerequisite names", () => {
    const lockedSkill: Skill = {
      ...baseSkill,
      id: "s5",
      name: "Hallucination Hunt",
      status: "locked",
      progress: undefined,
    };

    render(
      <SkillNode
        skill={lockedSkill}
        requires={["Swipe-Sort: AI or Not AI?"]}
      />
    );

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.getByText(/Locked/)).toBeInTheDocument();
    expect(
      screen.getByText("Requires: Swipe-Sort: AI or Not AI?")
    ).toBeInTheDocument();
  });

  it("calls onSelect with the skill when a clickable node is clicked", async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();

    render(<SkillNode skill={baseSkill} onSelect={onSelect} />);

    const button = screen.getByRole("button", {
      name: "Skill: Swipe-Sort: AI or Not AI?, Complete",
    });
    await user.click(button);

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith(baseSkill);
  });
});
