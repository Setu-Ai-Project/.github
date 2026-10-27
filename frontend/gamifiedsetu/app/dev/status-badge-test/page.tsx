import StatusBadge from "@/app/components/submission/StatusBadge";

export default function StatusBadgeTestPage() {
  return (
    <main className="min-h-screen bg-cream p-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <h1 className="font-display text-3xl font-bold text-ink">
          StatusBadge Test
        </h1>
        <div className="flex flex-wrap gap-3">
          <StatusBadge status="pending" />
          <StatusBadge status="passed" />
          <StatusBadge status="needs_revision" />
        </div>
      </div>
    </main>
  );
}