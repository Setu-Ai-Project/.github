import type { ProgressSnapshot } from "@/types/progress";
import XpBar from "./XpBar";

type ProgressDashboardProps = {
  snapshot: ProgressSnapshot;
};

export default function ProgressDashboard({ snapshot }: ProgressDashboardProps) {
  const totalSkills = snapshot.skills.length;
  const completedCount = snapshot.skills.filter(
    (skill) => skill.status === "complete"
  ).length;
  const inProgressSkills = snapshot.skills.filter(
    (skill) => skill.status === "in-progress"
  );

  return (
    <div className="flex flex-col rounded-2xl border-4 border-ink bg-cream p-5 shadow-[4px_4px_0_#172A32] w-full">
      <div className="mb-4 flex items-center justify-between">
        <span className="rounded-full border-2 border-ink bg-tealpop px-2.5 py-0.5 font-display text-xs font-bold text-ink">
          Level {snapshot.level}
        </span>
        <span className="font-display text-xs font-black text-ink">
          {snapshot.totalXp} XP total
        </span>
      </div>

      <XpBar current={snapshot.xpIntoLevel} max={snapshot.xpForNextLevel} />

      {totalSkills === 0 ? (
        <p className="mt-4 text-xs font-bold text-taskgray">
          Skills will appear here soon.
        </p>
      ) : (
        <div className="mt-4 border-t border-ink/10 pt-3">
          <p className="text-xs font-bold text-ink">
            {completedCount} of {totalSkills} skills complete
          </p>

          {inProgressSkills.length > 0 ? (
            <div className="mt-2 text-xs">
              <p className="font-bold text-taskgray">Keep going:</p>
              <ul className="mt-1 list-disc list-inside space-y-0.5 font-medium text-ink">
                {inProgressSkills.slice(0, 3).map((skill) => (
                  <li key={skill.id} className="truncate">
                    {skill.name}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="mt-2 text-xs font-bold text-taskgray">
              Nothing in progress right now.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
