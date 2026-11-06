import type {
  AnswerCheck,
  BuilderChallenge,
  LearnContent,
  Quiz,
  QuizQuestion,
} from "@/types/learning";

import {
  mockCheckAnswer,
  mockGetChallenge,
  mockGetLearnContent,
  mockGetQuiz,
} from "./mockLearning";

// Decide whether to use mock data or the real backend.
function shouldUseMock(): boolean {
  return (
    process.env.NEXT_PUBLIC_USE_MOCK === "true" ||
    !process.env.NEXT_PUBLIC_API_URL
  );
}

// Makes requests to the backend and handles failed responses.
async function requestJson(
  path: string,
  errorMessage: string,
  init?: RequestInit
): Promise<unknown> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured");
  }

  const response = await fetch(`${apiUrl}${path}`, init);

  if (!response.ok) {
    throw new Error(errorMessage);
  }

  return response.json();
}

// ASSUMPTION - confirm with Backend (SYNC 3)
type RawLesson = {
  id: number;
  module_id: number;
  title: string;
  sections: {
    heading: string;
    body: string;
  }[];
};

// ASSUMPTION - confirm with Backend (SYNC 3)
type RawQuiz = {
  id: number;
  module_id: number;
  title: string;
  questions: {
    id: number;
    question: string;
    options: string[];
  }[];
};

// ASSUMPTION - confirm with Backend (SYNC 3)
type RawChallenge = {
  id: number;
  module_id: number;
  title: string;
  goal: string;
  instructions: string;
  hints: string[];
};

// ASSUMPTION - confirm with Backend (SYNC 3)
type RawAnswerCheck = {
  correct: boolean;
  correct_index: number;
  explanation?: string;
};

// Convert backend lesson data into frontend format.
function toLearnContent(raw: RawLesson): LearnContent {
  return {
    id: String(raw.id),
    moduleId: String(raw.module_id),
    title: raw.title,
    sections: raw.sections,
  };
}

// Convert backend quiz data into frontend format.
// Correct answers are deliberately not included in quiz questions.
function toQuiz(raw: RawQuiz): Quiz {
  return {
    id: String(raw.id),
    moduleId: String(raw.module_id),
    title: raw.title,
    questions: raw.questions.map(
      (question): QuizQuestion => ({
        id: String(question.id),
        question: question.question,
        options: question.options,
      })
    ),
  };
}

// Convert backend challenge data into frontend format.
function toBuilderChallenge(raw: RawChallenge): BuilderChallenge {
  return {
    id: String(raw.id),
    moduleId: String(raw.module_id),
    title: raw.title,
    goal: raw.goal,
    instructions: raw.instructions,
    hints: raw.hints,
  };
}

// Convert backend answer-check data into frontend format.
function toAnswerCheck(raw: RawAnswerCheck): AnswerCheck {
  return {
    correct: raw.correct,
    correctIndex: raw.correct_index,
    explanation: raw.explanation,
  };
}

// Loads lesson content.
// async/await allows us to wait for the mock or backend response.
export async function getLearnContent(
  moduleId: string
): Promise<LearnContent> {
  if (shouldUseMock()) {
    return mockGetLearnContent(moduleId);
  }

  // ASSUMPTION - confirm with Backend (SYNC 3)
  const raw = (await requestJson(
    `/modules/${moduleId}/lesson`,
    "Could not load lesson"
  )) as RawLesson;

  return toLearnContent(raw);
}

// Loads quiz questions without exposing correct answers.
export async function getQuiz(moduleId: string): Promise<Quiz> {
  if (shouldUseMock()) {
    return mockGetQuiz(moduleId);
  }

  // ASSUMPTION - confirm with Backend (SYNC 3)
  const raw = (await requestJson(
    `/modules/${moduleId}/quiz`,
    "Could not load quiz"
  )) as RawQuiz;

  return toQuiz(raw);
}

// Loads a Builder Challenge.
export async function getBuilderChallenge(
  moduleId: string
): Promise<BuilderChallenge> {
  if (shouldUseMock()) {
    return mockGetChallenge(moduleId);
  }

  // ASSUMPTION - confirm with Backend (SYNC 3)
  const raw = (await requestJson(
    `/modules/${moduleId}/challenge`,
    "Could not load challenge"
  )) as RawChallenge;

  return toBuilderChallenge(raw);
}

// Sends a selected quiz answer to be checked.
export async function checkAnswer(
  moduleId: string,
  questionId: string,
  selectedIndex: number
): Promise<AnswerCheck> {
  if (shouldUseMock()) {
    return mockCheckAnswer(moduleId, questionId, selectedIndex);
  }

  // ASSUMPTION - confirm with Backend (SYNC 3)
  const raw = (await requestJson(
    `/modules/${moduleId}/quiz/check`,
    "Could not check answer",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question_id: Number(questionId),
        selected_index: selectedIndex,
      }),
    }
  )) as RawAnswerCheck;

  return toAnswerCheck(raw);
}