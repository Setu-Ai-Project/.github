'use client';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BugTooltipProps {
  message: string;
  onDismiss: () => void;
}

export default function BugTooltip({ message, onDismiss }: BugTooltipProps) {
  const [dismissing, setDismissing] = useState(false);
  const [removed, setRemoved] = useState(false);

  if (removed) return null;

  return (
    <AnimatePresence onExitComplete={() => setRemoved(true)}>
      {!dismissing ? (
        // Idle state: show bug-mascot.svg
        <motion.div
          key="idle"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.2 }}
          className="relative flex items-center gap-3 rounded-xl bg-cream p-4 shadow-hard border-2 border-ink"
        >
          <img src="/mascots/bug-mascot.svg" alt="Bug" className="w-10 h-10" />
          <p className="text-ink text-sm flex-1">{message}</p>
          <button
            onClick={() => {
              setDismissing(true);
              onDismiss();
            }}
            className="ml-2 text-ink/60 hover:text-ink"
          >
            ✕
          </button>
        </motion.div>
      ) : (
        // Dismissed state: show bug-dismissed.svg, then exit
        <motion.div
          key="dismissed"
          initial={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.2 }}
          className="relative flex items-center gap-3 rounded-xl bg-cream p-4 shadow-hard border-2 border-ink"
        >
          <img src="/mascots/bug-dismissed.svg" alt="Bug dismissed" className="w-10 h-10" />
          <p className="text-ink text-sm flex-1">{message}</p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}