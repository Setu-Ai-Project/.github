import type { ProgressSnapshot, Skill } from "@/types/progress";
import { levelProgress } from "@/utils/levels";
import { fakeNetwork } from "./mockHelpers";

// Flip to true only locally to test error states. Never commit it as true.
export const MOCK_FORCE_ERROR = false;
// How long the fake server "thinks" before answering, in milliseconds.
export const MOCK_DELAY_MS = 400;

const STARTING_XP = 50;

// The backend's seeded sub-modules, one skill each, worth 50 XP.
function createStartingState(): ProgressSnapshot {
  const skills: Skill[] = [
    {
      id: "s1",
      name: "Swipe-Sort: AI or Not AI?",
      description: "Sort everyday gadgets into AI and not AI.",
      moduleId: "1",
      status: "complete",
      prerequisites: [],
      xpReward: 50,
      progress: 100,
    },
    {
      id: "s2",
      name: "AI History Timeline",
      description: "Travel through the big moments that shaped AI.",
      moduleId: "1",
      status: "in-progress",
      prerequisites: [],
      xpReward: 50,
      progress: 40,
    },
    {
      id: "s3",
      name: "Case Study: DeepMind & the NHS",
      description: "See how AI helped doctors, and why privacy matters.",
      moduleId: "1",
      status: "in-progress",
      prerequisites: [],
      xpReward: 50,
      progress: 0,
    },
    {
      id: "s4",
      name: "Biased Dataset Sandbox",
      description: "Find out how unfair data leads to unfair AI.",
      moduleId: "1",
      status: "in-progress",
      prerequisites: [],
      xpReward: 50,
      progress: 0,
    },
    {
      id: "s5",
      name: "Hallucination Hunt",
      description: "Catch an AI confidently making things up.",
      moduleId: "2",
      status: "locked",
      prerequisites: ["s1", "s2"],
      xpReward: 50,
    },
    {
      id: "s6",
      name: "Prompt Lab",
      description: "Write prompts that get exactly what you want.",
      moduleId: "2",
      status: "locked",
      prerequisites: ["s2", "s3"],
      xpReward: 50,
    },
    {
      id: "s7",
      name: "Case Study: Mata v. Avianca",
      description: "Learn from lawyers who trusted fake AI answers.",
      moduleId: "2",
      status: "locked",
      prerequisites: ["s4"],
      xpReward: 50,
    },
    {
      id: "s8",
      name: "Build Your MVP Chatbot",
      description: "Design a simple chatbot that solves a real problem.",
      moduleId: "3",
      status: "locked",
      prerequisites: ["s5", "s6"],
      xpReward: 50,
    },
    {
      id: "s9",
      name: "Lean Canvas Workshop",
      description: "Plan your AI idea on a one-page business canvas.",
      moduleId: "3",
      status: "locked",
      prerequisites: ["s6"],
      xpReward: 50,
    },
    {
      id: "s10",
      name: "Record Your Pitch",
      description: "Present your idea in a short, confident pitch.",
      moduleId: "3",
      status: "locked",
      prerequisites: ["s7"],
      xpReward: 50,
    },
  ];

  return { totalXp: STARTING_XP, ...levelProgress(STARTING_XP), skills };
}

// The fake server's data. It lives in memory, so it resets when the page reloads.
let state = createStartingState();

// A pure function: every locked skill whose prerequisites all exist and are all
// complete becomes in-progress. A prerequisite id that doesn't exist keeps it locked.
export function unlockReadySkills(skills: Skill[]): Skill[] {
  const completeIds = new Set(
    skills.filter((skill) => skill.status === "complete").map((skill) => skill.id)
  );

  return skills.map((skill) =>
    skill.status === "locked" && skill.prerequisites.every((id) => completeIds.has(id))
      ? { ...skill, status: "in-progress", progress: 0 }
      : skill
  );
}

// Returns a deep copy, like a real server sending brand-new data each time.
// (If screens got the same object, React might not notice it changed.)
export function getMockProgress(): ProgressSnapshot {
  return structuredClone(state);
}

// What progressApi calls in mock mode: waits like a network, then answers.
export async function mockFetchProgress(): Promise<ProgressSnapshot> {
  await fakeNetwork(MOCK_DELAY_MS, MOCK_FORCE_ERROR);
  return getMockProgress();
}

// DEV ONLY: pretends the learner just finished an in-progress skill.
// Returns false (and changes nothing) for a missing or not-in-progress skill.
export function simulateCompleteChallenge(skillId: string): boolean {
  const target = state.skills.find((skill) => skill.id === skillId);
  if (!target || target.status !== "in-progress") return false;

  const totalXp = state.totalXp + target.xpReward;
  const skills = state.skills.map((skill) =>
    skill.id === skillId ? { ...skill, status: "complete" as const, progress: 100 } : skill
  );

  state = { totalXp, ...levelProgress(totalXp), skills: unlockReadySkills(skills) };
  return true;
}

// Puts the fake server back to its starting state.
export function resetMockProgress(): void {
  state = createStartingState();
}
