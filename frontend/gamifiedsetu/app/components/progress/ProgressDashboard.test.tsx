import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import type { ProgressSnapshot, Skill } from "@/types/progress";
import ProgressDashboard from "./ProgressDashboard";

function makeSkill(
  id: string,
  name: string,
  status: Skill["status"]
): Skill {
  return {
    id,
    name,
    description: `Desc ${name}`,
    moduleId: "1",
    status,
    prerequisites: [],
    xpReward: 50,
  };
}

describe("ProgressDashboard", () => {
  it("displays level, total XP, completed count, and in-progress skill names", () => {
    const skills: Skill[] = [
      makeSkill("s1", "Skill 1", "complete"),
      makeSkill("s2", "Skill 2", "complete"),
      makeSkill("s3", "Skill 3", "complete"),
      makeSkill("s4", "Skill 4", "in-progress"),
      makeSkill("s5", "Skill 5", "in-progress"),
      makeSkill("s6", "Skill 6", "locked"),
      makeSkill("s7", "Skill 7", "locked"),
      makeSkill("s8", "Skill 8", "locked"),
      makeSkill("s9", "Skill 9", "locked"),
      makeSkill("s10", "Skill 10", "locked"),
    ];

    const snapshot: ProgressSnapshot = {
      totalXp: 100,
      level: 2,
      xpIntoLevel: 0,
      xpForNextLevel: 150,
      skills,
    };

    render(<ProgressDashboard snapshot={snapshot} />);

    expect(screen.getByText("Level 2")).toBeInTheDocument();
    expect(screen.getByText("100 XP total")).toBeInTheDocument();
    expect(screen.getByText("3 of 10 skills complete")).toBeInTheDocument();
    expect(screen.getByText("Keep going:")).toBeInTheDocument();
    expect(screen.getByText("Skill 4")).toBeInTheDocument();
    expect(screen.getByText("Skill 5")).toBeInTheDocument();
  });

  it("shows 'Nothing in progress right now.' when there are no in-progress skills", () => {
    const snapshot: ProgressSnapshot = {
      totalXp: 50,
      level: 1,
      xpIntoLevel: 50,
      xpForNextLevel: 100,
      skills: [
        makeSkill("s1", "Skill 1", "complete"),
        makeSkill("s2", "Skill 2", "locked"),
      ],
    };

    render(<ProgressDashboard snapshot={snapshot} />);

    expect(
      screen.getByText("Nothing in progress right now.")
    ).toBeInTheDocument();
  });

  it("shows 'Skills will appear here soon.' when skills array is empty", () => {
    const snapshot: ProgressSnapshot = {
      totalXp: 0,
      level: 1,
      xpIntoLevel: 0,
      xpForNextLevel: 100,
      skills: [],
    };

    render(<ProgressDashboard snapshot={snapshot} />);

    expect(
      screen.getByText("Skills will appear here soon.")
    ).toBeInTheDocument();
  });
});
