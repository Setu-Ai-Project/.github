"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import type { Mode } from "@/types/doubt";

type ModeContextValue = {
  mode: Mode;
  setMode: (mode: Mode) => void;
};

// null means "no ModeProvider above me"; useMode() turns that into a clear error.
const ModeContext = createContext<ModeContextValue | null>(null);

type ModeProviderProps = {
  children: ReactNode;
  initialMode?: Mode;
};

// Wrap a page in this so every component inside can read and change the mode.
export function ModeProvider({ children, initialMode = "learner" }: ModeProviderProps) {
  const [mode, setMode] = useState<Mode>(initialMode);

  return <ModeContext.Provider value={{ mode, setMode }}>{children}</ModeContext.Provider>;
}

// Shortcut for components: const { mode, setMode } = useMode();
export function useMode() {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error("useMode must be used inside <ModeProvider>");
  }
  return context;
}
