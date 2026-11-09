
import type { LessonSection as LessonSectionType } from "@/types/learning";

type LessonSectionProps = {
  section: LessonSectionType;
};

export default function LessonSection({
  section,
}: LessonSectionProps) {
  return (
    <section className="rounded-xl border border-ink/10 bg-white p-5 shadow-sm">
      <h2 className="mb-3 font-display text-xl font-bold text-ink">
        {section.heading}
      </h2>

      <p className="max-w-prose whitespace-pre-line break-words text-base leading-relaxed text-ink">
        {section.body}
      </p>
    </section>
  );
}
