"use client";

import Image from "next/image";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

type BugTooltipProps = {
  message: string;
  onDismiss: () => void;
};

export default function BugTooltip({ message, onDismiss }: BugTooltipProps) {
  const [dismissed, setDismissed] = useState(false);
  const [visible, setVisible] = useState(true);

  function handleDismiss() {
    setDismissed(true);
    onDismiss();
    window.setTimeout(() => setVisible(false), 0);
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92, y: 8 }}
          transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
          className="relative flex w-full max-w-sm items-center gap-3 border-2 border-[#173d35] bg-[#fff8e8] px-4 py-3 text-[#173d35] shadow-[5px_5px_0_#173d35]"
        >
          <div className="relative h-16 w-16 shrink-0">
            <Image
              src={dismissed ? "/mascots/bug-dismissed.svg" : "/mascots/bug-mascot.svg"}
              alt=""
              fill
              className="object-contain"
              sizes="64px"
            />
          </div>
          <p className="min-w-0 flex-1 text-sm font-semibold leading-5">{message}</p>
          {!dismissed && (
            <button
              type="button"
              onClick={handleDismiss}
              aria-label="Dismiss message"
              className="grid h-7 w-7 shrink-0 place-items-center border-2 border-[#173d35] text-lg font-bold leading-none transition-transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <span aria-hidden="true">x</span>
            </button>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}