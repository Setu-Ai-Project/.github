import QuizScreen from "@/app/components/quiz/QuizScreen";

type QuizPageProps = {
  params: Promise<{
    moduleId: string;
  }>;
};

export default async function QuizPage({ params }: QuizPageProps) {
  const { moduleId } = await params;

  return <QuizScreen moduleId={moduleId} />;
}
