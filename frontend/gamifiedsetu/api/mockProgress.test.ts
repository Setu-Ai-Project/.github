import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { Skill } from "@/types/progress";
import {
  MOCK_DELAY_MS,
  getMockProgress,
  mockFetchProgress,
  resetMockProgress,
  simulateCompleteChallenge,
  unlockReadySkills,
} from "./mockProgress";

// Looks up one skill's status in the current mock state.
function statusOf(id: string) {
  return getMockProgress().skills.find((skill) => skill.id === id)?.status;
}

beforeEach(() => {
  resetMockProgress();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("mock progress starting state", () => {
  it("starts with the 10 seeded skills, 50 XP and level 1", () => {
    const progress = getMockProgress();

    expect(progress.skills).toHaveLength(10);
    expect(statusOf("s1")).toBe("complete");
    for (const id of ["s2", "s3", "s4"]) expect(statusOf(id)).toBe("in-progress");
    for (const id of ["s5", "s6", "s7", "s8", "s9", "s10"]) expect(statusOf(id)).toBe("locked");
    expect(progress.totalXp).toBe(50);
    expect(progress.level).toBe(1);
  });

  it("returns a copy, so changing it doesn't change the mock", () => {
    const first = getMockProgress();
    first.totalXp = 9999;
    first.skills[0].status = "locked";

    const second = getMockProgress();
    expect(second.totalXp).toBe(50);
    expect(second.skills[0].status).toBe("complete");
  });
});

describe("simulateCompleteChallenge", () => {
  it("completes the skill, adds XP, levels up and unlocks what's ready", () => {
    expect(simulateCompleteChallenge("s2")).toBe(true);

    const progress = getMockProgress();
    expect(statusOf("s2")).toBe("complete");
    expect(progress.totalXp).toBe(100);
    expect(progress.level).toBe(2);
    expect(progress.xpIntoLevel).toBe(0);
    expect(progress.xpForNextLevel).toBe(150);
    // s5 needs s1 + s2, both complete now.
    expect(statusOf("s5")).toBe("in-progress");
    // s6 still needs s3.
    expect(statusOf("s6")).toBe("locked");
  });

  it("changes nothing for a locked or unknown skill", () => {
    const before = getMockProgress();

    expect(simulateCompleteChallenge("s5")).toBe(false);
    expect(simulateCompleteChallenge("nope")).toBe(false);
    expect(getMockProgress()).toEqual(before);
  });

  it("resets back to the starting state", () => {
    simulateCompleteChallenge("s2");
    resetMockProgress();

    expect(getMockProgress().totalXp).toBe(50);
    expect(statusOf("s2")).toBe("in-progress");
  });
});

describe("unlockReadySkills", () => {
  const skill = (id: string, status: Skill["status"], prerequisites: string[] = []): Skill => ({
    id,
    name: id,
    description: "",
    moduleId: "1",
    status,
    prerequisites,
    xpReward: 50,
  });

  it("keeps a skill locked when a prerequisite doesn't exist", () => {
    const result = unlockReadySkills([skill("a", "complete"), skill("b", "locked", ["a", "ghost"])]);
    expect(result[1].status).toBe("locked");
  });

  it("unlocks a skill once all its prerequisites are complete", () => {
    const result = unlockReadySkills([skill("a", "complete"), skill("b", "locked", ["a"])]);
    expect(result[1]).toMatchObject({ status: "in-progress", progress: 0 });
  });
});

describe("mockFetchProgress", () => {
  it("answers only after the fake network delay", async () => {
    vi.useFakeTimers();
    let resolved = false;
    const promise = mockFetchProgress().then((result) => {
      resolved = true;
      return result;
    });

    await vi.advanceTimersByTimeAsync(MOCK_DELAY_MS - 1);
    expect(resolved).toBe(false);

    await vi.advanceTimersByTimeAsync(1);
    expect((await promise).totalXp).toBe(50);
    expect(resolved).toBe(true);
  });
});
