// Copied from backend/config/progression_rules.py. Keep the two in sync.
// Level N starts at this much total XP.
export const LEVEL_THRESHOLDS: Record<number, number> = { 1: 0, 2: 100, 3: 250, 4: 500, 5: 1000 };
export const MAX_LEVEL = 5;

export type LevelProgress = { level: number; xpIntoLevel: number; xpForNextLevel: number };

// A pure function: works out the level and how far into it a learner is, from total XP alone.
export function levelProgress(totalXp: number): LevelProgress {
  const xp = Math.max(0, totalXp);

  // The highest level whose starting XP we have reached.
  let level = 1;
  for (let lvl = 1; lvl <= MAX_LEVEL; lvl++) {
    if (xp >= LEVEL_THRESHOLDS[lvl]) level = lvl;
  }

  const xpIntoLevel = xp - LEVEL_THRESHOLDS[level];
  // At the max level there is no next level, so the level has no size.
  const xpForNextLevel =
    level >= MAX_LEVEL ? 0 : LEVEL_THRESHOLDS[level + 1] - LEVEL_THRESHOLDS[level];

  return { level, xpIntoLevel, xpForNextLevel };
}
