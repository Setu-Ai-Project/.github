import type { Skill } from "@/types/progress";

// Groups skills into tiers based on prerequisites.
// Tier 1 has no prerequisites (or only missing ones).
// Each subsequent tier depends on skills in previous tiers.
export function computeTiers(skills: Skill[]): Skill[][] {
  const skillMap = new Map<string, Skill>();
  for (const skill of skills) {
    skillMap.set(skill.id, skill);
  }

  const memo = new Map<string, number>();
  const visiting = new Set<string>();

  function getTier(skillId: string): number {
    if (memo.has(skillId)) return memo.get(skillId)!;
    if (visiting.has(skillId)) {
      // Cycle detected: treat this link as tier 0 to prevent infinite recursion
      return 0;
    }

    const skill = skillMap.get(skillId);
    if (!skill) {
      // Prerequisite not in skills list: ignored
      return 0;
    }

    visiting.add(skillId);
    let maxPrereqTier = 0;
    for (const prereqId of skill.prerequisites) {
      if (skillMap.has(prereqId)) {
        const pTier = getTier(prereqId);
        if (pTier > maxPrereqTier) {
          maxPrereqTier = pTier;
        }
      }
    }
    visiting.delete(skillId);

    const tier = 1 + maxPrereqTier;
    memo.set(skillId, tier);
    return tier;
  }

  const tierGroups = new Map<number, Skill[]>();
  let maxTier = 0;

  for (const skill of skills) {
    const tier = getTier(skill.id);
    if (tier > maxTier) {
      maxTier = tier;
    }
    if (!tierGroups.has(tier)) {
      tierGroups.set(tier, []);
    }
    tierGroups.get(tier)!.push(skill);
  }

  const result: Skill[][] = [];
  for (let t = 1; t <= maxTier; t++) {
    const group = tierGroups.get(t);
    if (group && group.length > 0) {
      result.push(group);
    }
  }

  return result;
}
