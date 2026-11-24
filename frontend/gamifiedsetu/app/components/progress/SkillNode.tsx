"use client";

import { motion } from "motion/react";
import type { Skill, SkillStatus } from "@/types/progress";

const STATUS_LABEL: Record<SkillStatus, string> = {
  locked: "Locked",
  "in-progress": "In progress",
  complete: "Complete",
};

type SkillNodeProps = {
  skill: Skill;
  requires?: string[];
  onSelect?: (skill: Skill) => void;
};

export default function SkillNode({ skill, requires = [], onSelect }: SkillNodeProps) {
  const isLocked = skill.status === "locked";
  const isComplete = skill.status === "complete";
  const isInProgress = skill.status === "in-progress";

  if (isLocked) {
    const requirementText =
      requires.length > 0
        ? `Requires: ${requires.join(", ")}`
        : "Finish earlier skills first";

    return (
      <div className="flex flex-col justify-between rounded-2xl border-4 border-dashed border-ink bg-white p-4 text-left opacity-60 shadow-[4px_4px_0_#172A32] text-taskgray w-full">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="font-display text-xs font-bold uppercase tracking-wider text-taskgray">
              🔒 {STATUS_LABEL.locked}
            </span>
          </div>
          <h3 className="font-display text-lg font-bold break-words text-taskgray">
            {skill.name}
          </h3>
          <p className="mt-1 text-xs text-taskgray">
            {skill.description}
          </p>
        </div>

        <div className="mt-4 border-t border-ink/20 pt-3">
          <p className="text-xs font-semibold text-taskgray break-words">
            {requirementText}
          </p>
        </div>
      </div>
    );
  }

  const progressValue = skill.progress ?? 0;

  return (
    <motion.button
      type="button"
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      aria-label={`Skill: ${skill.name}, ${STATUS_LABEL[skill.status]}`}
      onClick={() => onSelect?.(skill)}
      className={`flex flex-col justify-between rounded-2xl border-4 border-ink p-4 text-left shadow-[4px_4px_0_#172A32] w-full transition-shadow hover:shadow-[6px_6px_0_#172A32] ${
        isComplete ? "bg-tealpop text-ink" : "bg-white text-ink"
      }`}
    >
      <div>
        <div className="mb-2 flex items-center justify-between">
          <span className="rounded-full border-2 border-ink bg-white/80 px-2.5 py-0.5 font-display text-xs font-bold text-ink">
            {isComplete ? `✓ ${STATUS_LABEL.complete}` : STATUS_LABEL["in-progress"]}
          </span>
          {isComplete && (
            <span className="font-display text-xs font-black text-ink">
              +{skill.xpReward} XP
            </span>
          )}
        </div>
        <h3 className="font-display text-lg font-bold break-words text-ink">
          {skill.name}
        </h3>
        <p className="mt-1 text-xs text-taskgray">
          {skill.description}
        </p>
      </div>

      {isInProgress && (
        <div className="mt-4 border-t border-ink/10 pt-3 w-full">
          <div className="flex items-center justify-between text-xs font-bold text-ink">
            <span>{STATUS_LABEL["in-progress"]}</span>
            <span>{progressValue}% done</span>
          </div>
          <div className="mt-2 h-2 w-full overflow-hidden rounded-full border-2 border-ink bg-cream/60">
            <div
              className="h-full bg-coral transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(0, progressValue))}%` }}
            />
          </div>
        </div>
      )}
    </motion.button>
  );
}
