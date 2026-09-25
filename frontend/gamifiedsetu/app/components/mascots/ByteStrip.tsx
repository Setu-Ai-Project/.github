"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { AnimatePresence, motion } from "motion/react";

type ByteStripProps = {
  message: string;
  onDismiss: () => void;
};

export default function ByteStrip({ message, onDismiss }: ByteStripProps) {
  const [dismissed, setDismissed] = useState(false);
  const [removed, setRemoved] = useState(false);
  const removeTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (removeTimeout.current) {
        clearTimeout(removeTimeout.current);
      }
    };
  }, []);

  const handleDismiss = () => {
    setDismissed(true);
    removeTimeout.current = setTimeout(() => {
      setRemoved(true);
    }, 150);
    onDismiss();
  };

  return (
    <AnimatePresence>
      {!removed && (
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="relative flex w-full items-center gap-3 rounded-2xl border-4 border-ink bg-white px-4 py-3 shadow-[8px_8px_0_#172A32]"
        >
          <Image
            src={
              dismissed
                ? "/mascots/byte-dismissed.svg"
                : "/mascots/byte-mascot.svg"
            }
            alt={dismissed ? "Byte the robot dismissed" : "Byte the robot mascot"}
            width={56}
            height={56}
            className="h-14 w-14 shrink-0"
          />

          <p className="flex-1 font-display text-base text-ink">
            {message}
          </p>

          {!dismissed && (
            <button
              type="button"
              onClick={handleDismiss}
              aria-label="Dismiss Byte"
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 border-ink bg-cream text-base font-bold text-ink transition-transform hover:-translate-y-0.5"
            >
              ×
            </button>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
