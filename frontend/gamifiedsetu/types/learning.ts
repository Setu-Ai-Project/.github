
// ASSUMPTION - confirm with Backend (SYNC 3)

export type LessonSection = {
  heading: string;
  body: string;
};

export type LearnContent = {
  id: string;
  moduleId: string;
  title: string;
  sections: LessonSection[];
};

export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
  // The backend may not send correctIndex.
  // Screens must never read it; use checkAnswer instead.
  correctIndex?: number;
  explanation?: string;
};

export type Quiz = {
  id: string;
  moduleId: string;
  title: string;
  questions: QuizQuestion[];
};

export type BuilderChallenge = {
  id: string;
  moduleId: string;
  title: string;
  goal: string;
  instructions: string;
  hints: string[];
};

export type AnswerCheck = {
  correct: boolean;
  correctIndex: number;
  explanation?: string;
};
