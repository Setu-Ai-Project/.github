
import LearnScreen from "@/app/components/learning/LearnScreen";

type LearnPageProps = {
  params: Promise<{
    moduleId: string;
  }>;
};

export default async function LearnPage({ params }: LearnPageProps) {
  const { moduleId } = await params;

  return <LearnScreen moduleId={moduleId} />;
}
