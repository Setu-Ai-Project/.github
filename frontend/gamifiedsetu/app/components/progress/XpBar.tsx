"use client";

import { motion } from "motion/react";

type XpBarProps = {
  current: number;
  max: number;
};

export default function XpBar({ current, max }: XpBarProps) {
  const percent =
    max > 0 ? Math.min(100, Math.max(0, (current / max) * 100)) : 100;

  return (
    <div className="w-full">
      <div
        role="progressbar"
        aria-label="XP progress to the next level"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(percent)}
        className="h-4 w-full overflow-hidden rounded-full border-2 border-ink bg-white"
      >
        <motion.div
          className="h-full bg-tealpop"
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      </div>

      <p className="mt-2 text-xs font-bold text-taskgray">
        {max === 0 ? "Max level!" : `${current} / ${max} XP`}
      </p>
    </div>
  );
}
