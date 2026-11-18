import { describe, expect, it } from "vitest";

import { levelProgress } from "./levels";

describe("levelProgress", () => {
  it("starts a brand-new learner at level 1", () => {
    expect(levelProgress(0)).toEqual({ level: 1, xpIntoLevel: 0, xpForNextLevel: 100 });
  });

  it("works out the level and how far into it the learner is", () => {
    expect(levelProgress(50)).toEqual({ level: 1, xpIntoLevel: 50, xpForNextLevel: 100 });
    expect(levelProgress(100)).toEqual({ level: 2, xpIntoLevel: 0, xpForNextLevel: 150 });
    expect(levelProgress(260)).toEqual({ level: 3, xpIntoLevel: 10, xpForNextLevel: 250 });
  });

  it("handles the max level and negative XP", () => {
    expect(levelProgress(1200)).toEqual({ level: 5, xpIntoLevel: 200, xpForNextLevel: 0 });
    expect(levelProgress(-5)).toEqual({ level: 1, xpIntoLevel: 0, xpForNextLevel: 100 });
  });
});
