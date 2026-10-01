"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { AnimatePresence, motion } from "motion/react";

type NovaBannerProps = {
  message: string;
  onDismiss: () => void;
};

export default function NovaBanner({ message, onDismiss }: NovaBannerProps) {
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
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="relative flex w-full items-center gap-4 rounded-2xl border-4 border-ink bg-white p-4 shadow-[8px_8px_0_#172A32]"
        >
          <Image
            src={
              dismissed
                ? "/mascots/nova-dismissed.svg"
                : "/mascots/nova-mascot.svg"
            }
            alt={dismissed ? "Nova the robot dismissed" : "Nova the robot mascot"}
            width={64}
            height={64}
            className="h-16 w-16 shrink-0"
          />

          <p className="flex-1 font-display text-base text-ink">
            {message}
          </p>

          {!dismissed && (
            <button
              type="button"
              onClick={handleDismiss}
              aria-label="Dismiss Nova"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-ink bg-cream text-lg font-bold text-ink transition-transform hover:-translate-y-0.5"
            >
              ×
            </button>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}