"use client";

import ByteStrip from "../../components/mascots/ByteStrip";

export default function ByteTestPage() {
  return (
    <main className="min-h-screen bg-cream p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          ByteStrip Test
        </h1>

        <ByteStrip
          message="Tip: you can save your progress anytime."
          onDismiss={() => console.log("First ByteStrip dismissed")}
        />

        <ByteStrip
          message="Byte here — don't forget to try the quiz!"
          onDismiss={() => console.log("Second ByteStrip dismissed")}
        />
      </div>
    </main>
  );
}
