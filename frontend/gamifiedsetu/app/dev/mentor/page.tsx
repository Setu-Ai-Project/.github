"use client";

import { ModeProvider, useMode } from "@/context/ModeContext";
import ModeSwitch from "@/app/components/mentor-mode/ModeSwitch";
import MyDoubts from "@/app/components/mentor-mode/MyDoubts";
import MentorDashboard from "@/app/components/mentor-mode/MentorDashboard";

function Screen() {
  const { mode } = useMode();
  // Switching mode unmounts one view and mounts the other, and each loads fresh
  // data when it appears — that's how the learner sees a new reply right away.
  return mode === "learner" ? <MyDoubts /> : <MentorDashboard />;
}

export default function MentorModePage() {
  return (
    <ModeProvider>
      <main className="min-h-screen bg-cream px-4 py-10">
        <div className="mx-auto flex max-w-2xl flex-col gap-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h1 className="font-display text-3xl font-bold text-ink">Mentor Mode</h1>
            <ModeSwitch />
          </div>
          <Screen />
        </div>
      </main>
    </ModeProvider>
  );
}
