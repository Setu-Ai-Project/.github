"use client";

import { useState } from "react";
import Image from "next/image";
import { AnimatePresence, motion } from "motion/react";

type SparkCardProps = {
  message: string;
  onDismiss: () => void;
};

export default function SparkCard({
  message,
  onDismiss,
}: SparkCardProps) {
  const [dismissed, setDismissed] = useState(false);

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss();
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{
          opacity: dismissed ? 0 : 1,
          y: dismissed ? 40 : 0,
        }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="relative flex items-center gap-4 rounded-3xl border-4 border-ink bg-white p-6 shadow-[8px_8px_0_#172A32]"
      >
        <Image
          src={
            dismissed
              ? "/mascots/spark-dismissed.svg"
              : "/mascots/spark-mascot.svg"
          }
          alt={
            dismissed
              ? "Spark the lightbulb dismissed"
              : "Spark the lightbulb mascot"
          }
          width={100}
          height={100}
          className="h-24 w-24 shrink-0"
        />

        <div className="flex-1">
          <p className="font-display text-lg text-ink">
            {message}
          </p>
        </div>

        {!dismissed && (
          <button
            type="button"
            onClick={handleDismiss}
            aria-label="Dismiss Spark"
            className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full border-2 border-ink bg-cream text-lg font-bold text-ink transition-transform hover:-translate-y-0.5"
          >
            ×
          </button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}