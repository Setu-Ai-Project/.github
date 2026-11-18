import type { ProgressSnapshot, Skill, SkillStatus } from "@/types/progress";
import { levelProgress } from "@/utils/levels";
import { shouldUseMock } from "./mockHelpers";
import { mockFetchProgress } from "./mockProgress";

// The only file in Step 5 that talks to the backend.

// ASSUMPTION - confirm with Backend (SYNC 4). Today /progress/me sends total_xp,
// level, xp_to_next_level, badges and certificates, but NO skills yet.
type RawSkill = {
  id: number;
  name: string;
  description: string;
  module_id: number;
  status: SkillStatus;
  prerequisites: number[];
  xp_reward: number;
  progress?: number;
};
type RawProgress = { total_xp: number; skills?: RawSkill[] };

// Mapper: backend snake_case + number ids → our camelCase + string ids.
function toSkill(raw: RawSkill): Skill {
  return {
    id: String(raw.id),
    name: raw.name,
    description: raw.description,
    moduleId: String(raw.module_id),
    status: raw.status,
    prerequisites: raw.prerequisites.map(String),
    xpReward: raw.xp_reward,
    progress: raw.progress,
  };
}

function toSnapshot(raw: RawProgress): ProgressSnapshot {
  // The backend sends "XP still needed"; our bar needs "XP into the level" and
  // "level size", so we work them out from total XP with the backend's own thresholds.
  const { level, xpIntoLevel, xpForNextLevel } = levelProgress(raw.total_xp);
  return {
    totalXp: raw.total_xp,
    level,
    xpIntoLevel,
    xpForNextLevel,
    // No skills from the backend yet → an empty map instead of a crash.
    skills: raw.skills ? raw.skills.map(toSkill) : [],
  };
}

// `async` means this function may need to wait; `await` pauses until the answer arrives.
// `getToken` is only called in real mode, so mock mode never waits for login to load.
export async function fetchProgress(
  getToken?: () => Promise<string | null>
): Promise<ProgressSnapshot> {
  if (shouldUseMock()) return mockFetchProgress();

  const token = getToken ? await getToken() : null;
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/progress/me`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  // The learner has no account row yet: show zero progress, not an error.
  if (res.status === 404) return toSnapshot({ total_xp: 0 });
  if (!res.ok) throw new Error("Could not load progress");

  return toSnapshot((await res.json()) as RawProgress);
}
