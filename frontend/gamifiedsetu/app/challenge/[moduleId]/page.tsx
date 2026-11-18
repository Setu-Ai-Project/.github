import ChallengeScreen from "@/app/components/learning/ChallengeScreen";

type ChallengePageProps = {
  params: Promise<{
    moduleId: string;
  }>;
};

export default async function ChallengePage({ params }: ChallengePageProps) {
  const { moduleId } = await params;

  return <ChallengeScreen moduleId={moduleId} />;
}
