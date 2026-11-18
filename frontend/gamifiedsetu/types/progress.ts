// ASSUMPTION - replace with Backend's real contract (SYNC 4).

// The three states a skill can be in. The status words are written ONLY here;
// everything else imports this type. If Backend spells them differently, fix it here.
export type SkillStatus = "locked" | "in-progress" | "complete";

// One skill on the map (today: one seeded sub-module).
export type Skill = {
  id: string;
  name: string;
  description: string;
  // The module this skill belongs to. Clicking the skill opens /module/{moduleId}.
  moduleId: string;
  status: SkillStatus;
  // Ids of the skills that must be complete before this one unlocks.
  prerequisites: string[];
  xpReward: number;
  // 0-100. Only in-progress skills have it.
  progress?: number;
};

// Everything the Skill Map and the Dashboard need, at one moment in time.
export type ProgressSnapshot = {
  totalXp: number;
  level: number;
  // XP earned inside the current level.
  xpIntoLevel: number;
  // How big the current level is, in XP. 0 at the max level.
  xpForNextLevel: number;
  skills: Skill[];
};
