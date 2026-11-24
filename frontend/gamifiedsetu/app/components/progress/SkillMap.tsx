import type { Skill } from "@/types/progress";
import { computeTiers } from "@/utils/computeTiers";
import SkillNode from "./SkillNode";

type SkillMapProps = {
  skills: Skill[];
  onSelectSkill?: (skill: Skill) => void;
};

export default function SkillMap({ skills, onSelectSkill }: SkillMapProps) {
  if (skills.length === 0) {
    return (
      <div className="rounded-2xl border-4 border-ink bg-white p-8 text-center shadow-[4px_4px_0_#172A32]">
        <p className="font-display font-bold text-taskgray">
          Your skills will appear here soon.
        </p>
      </div>
    );
  }

  const skillById = new Map<string, Skill>(
    skills.map((skill) => [skill.id, skill])
  );

  const tiers = computeTiers(skills);

  return (
    <div className="flex flex-col gap-8 w-full">
      {tiers.map((tierSkills, tierIndex) => (
        <section key={tierIndex} className="flex flex-col gap-3">
          <h2 className="font-display font-bold text-xl text-ink">
            Tier {tierIndex + 1}
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tierSkills.map((skill) => {
              const requires =
                skill.status === "locked"
                  ? skill.prerequisites
                      .map((id) => skillById.get(id))
                      .filter((s): s is Skill => s !== undefined && s.status !== "complete")
                      .map((s) => s.name)
                  : undefined;

              return (
                <SkillNode
                  key={skill.id}
                  skill={skill}
                  requires={requires}
                  onSelect={onSelectSkill}
                />
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
