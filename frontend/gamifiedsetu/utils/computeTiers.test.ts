import { describe, expect, it } from "vitest";

import { getMockProgress } from "@/api/mockProgress";
import type { Skill } from "@/types/progress";
import { computeTiers } from "./computeTiers";

function createSkill(
  id: string,
  prerequisites: string[] = [],
  name: string = id
): Skill {
  return {
    id,
    name,
    description: `Description for ${name}`,
    moduleId: "1",
    status: "locked",
    prerequisites,
    xpReward: 50,
  };
}

describe("computeTiers", () => {
  it("groups the 10 mock skills into tier sizes [4, 3, 3] with s5, s6, s7 in tier 2", () => {
    const { skills } = getMockProgress();
    const tiers = computeTiers(skills);

    expect(tiers.map((tier) => tier.length)).toEqual([4, 3, 3]);

    const tier2Ids = tiers[1].map((skill) => skill.id);
    expect(tier2Ids).toEqual(["s5", "s6", "s7"]);
  });

  it("places a skill with a nonexistent prerequisite in tier 1 without crashing", () => {
    const skills: Skill[] = [
      createSkill("s1", ["nonexistent-id"]),
      createSkill("s2", []),
    ];

    const tiers = computeTiers(skills);
    expect(tiers).toHaveLength(1);
    expect(tiers[0].map((s) => s.id)).toEqual(["s1", "s2"]);
  });

  it("handles dependency cycles without hanging and includes each skill exactly once", () => {
    const skills: Skill[] = [
      createSkill("a", ["b"]),
      createSkill("b", ["a"]),
    ];

    const tiers = computeTiers(skills);
    const flattened = tiers.flat();

    expect(flattened).toHaveLength(2);
    const ids = flattened.map((s) => s.id);
    expect(ids).toContain("a");
    expect(ids).toContain("b");
    expect(new Set(ids).size).toBe(2);
  });

  it("preserves the original skill order within each tier", () => {
    const skills: Skill[] = [
      createSkill("alpha", []),
      createSkill("beta", []),
      createSkill("gamma", []),
      createSkill("delta", ["alpha"]),
      createSkill("epsilon", ["beta"]),
    ];

    const tiers = computeTiers(skills);
    expect(tiers[0].map((s) => s.id)).toEqual(["alpha", "beta", "gamma"]);
    expect(tiers[1].map((s) => s.id)).toEqual(["delta", "epsilon"]);
  });
});
