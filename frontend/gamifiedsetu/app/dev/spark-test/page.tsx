"use client";

import SparkCard from "../../components/mascots/SparkCard";

export default function SparkTestPage() {
  return (
    <main className="min-h-screen bg-cream p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          SparkCard Test
        </h1>

        <SparkCard
          message="Welcome! I'm Spark, and I'll help you understand AI."
          onDismiss={() => console.log("First SparkCard dismissed")}
        />

        <SparkCard
          message="Remember, mistakes are part of learning!"
          onDismiss={() => console.log("Second SparkCard dismissed")}
        />
      </div>
    </main>
  );
}