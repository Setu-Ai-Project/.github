
// These settings help us simulate a backend while developing.
export const MOCK_FORCE_ERROR = false;
export const MOCK_DELAY_MS = 600;
export const MOCK_CHECK_DELAY_MS = 300;

// Sample lesson content for module 1: What Is AI?
export const mockLearn = {
  id: "1",
  moduleId: "1",
  title: "What Is AI?",
  sections: [
    {
      heading: "Swipe-Sort: AI or Not AI?",
      
      
body: "Artificial Intelligence (AI) is technology that enables computers to perform tasks that usually require human intelligence. These tasks include recognising pictures, understanding spoken or written language, finding patterns, solving problems and making predictions. However, not every digital device uses AI. A basic calculator follows fixed instructions to perform calculations, while an AI-powered photo app may analyse an image and identify objects such as people, animals or trees. This difference is important because it helps us recognise when a machine is simply following a set of rules and when it is using patterns learned from data. AI already appears in many everyday tools, including navigation apps, recommendation systems and voice assistants. As you explore this topic, think about the technology you use at home or school. Ask what information it receives, what task it performs and whether it adapts its results based on patterns. Remember that AI can be useful, but its results still need to be checked by people."

    },
    {
      heading: "AI History Timeline",
      body: "AI has developed over many decades. Early researchers explored whether machines could imitate aspects of human thinking. Over time, computers became more powerful and researchers developed new ways for machines to learn from data."
    },
    {
      heading: "Case Study: DeepMind & the NHS",
      body: "This case study explores how AI research can support healthcare. DeepMind worked with the NHS on technology intended to help healthcare professionals identify signs of certain eye conditions. It also raises important questions about patient privacy, data protection and responsible use of health information."
    },
    {
      heading: "Biased Dataset Sandbox",
      body: "Data can be biased."
    }
  ]
};

// Sample quiz for module 1.
export const mockQuiz = {
  id: "1",
  moduleId: "1",
  title: "What Is AI? Quiz",
  questions: [
    {
      id: "1",
      question: "What does Artificial Intelligence enable computers to do?",
      options: [
        "Perform tasks that usually require human intelligence",
        "Work without electricity",
        "Replace every human decision"
      ],
      correctIndex: 0,
      explanation: "AI enables computers to perform tasks such as recognising patterns, understanding language and solving problems."
    },
    {
      id: "2",
      question: "Why is an AI history timeline useful?",
      options: [
        "It shows how AI has developed over time",
        "It lists every computer ever made",
        "It explains how to build a mobile phone",
        "It shows only the latest AI tools"
      ],
      correctIndex: 0,
      explanation: "A timeline helps us understand important developments in AI research."
    },
    {
      id: "3",
      question: "What is one important concern when AI is used in healthcare?",
      options: [
        "Patient privacy and data protection",
        "The colour of hospital walls",
        "The size of a computer screen"
      ],
      correctIndex: 0,
      explanation: "Healthcare information is sensitive, so patient privacy and responsible data use matter."
    },
    {
      id: "4",
      question: "What can happen when an AI system is trained using biased data?",
      options: [
        "It may produce unfair results",
        "It will always become more accurate",
        "It will stop using data",
        "It will automatically remove all errors"
      ],
      correctIndex: 0,
      explanation: "Biased training data can lead an AI system to produce unfair or unreliable results."
    }
  ]
};

// Sample Builder Challenge for module 1.
export const mockChallenge = {
  id: "1",
  moduleId: "1",
  title: "Describe a sunset",
  goal: "Write a description of a sunset using at least eight words that communicate a clear mood and style.",
  instructions: "1. Imagine a sunset you would like to describe.\n2. Choose words that help communicate its colours and atmosphere.\n3. Write at least eight words in a description.\n4. Make sure your description communicates a mood and a style.",
  hints: [
    "Think about the colours in the sky and how they make the scene feel.",
    "Choose descriptive words that create a consistent mood and writing style."
  ]
};
// Simulates a network request and can force an error for testing.
async function fakeNetwork(delay: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, delay));

  if (MOCK_FORCE_ERROR) {
    throw new Error("Mock server is down");
  }
}

// Loads the lesson content for a module.
export async function mockGetLearnContent(moduleId: string) {
  await fakeNetwork(MOCK_DELAY_MS);

  if (moduleId !== "1") {
    throw new Error("Module not found");
  }

  return mockLearn;
}

// Loads the quiz for a module.
export async function mockGetQuiz(moduleId: string) {
  await fakeNetwork(MOCK_DELAY_MS);

  if (moduleId !== "1") {
    throw new Error("Module not found");
  }

  return mockQuiz;
}

// Loads the Builder Challenge for a module.
export async function mockGetChallenge(moduleId: string) {
  await fakeNetwork(MOCK_DELAY_MS);

  if (moduleId !== "1") {
    throw new Error("Module not found");
  }

  return mockChallenge;
}

// Checks a learner's selected quiz answer.
export async function mockCheckAnswer(
  moduleId: string,
  questionId: string,
  selectedIndex: number
) {
  await fakeNetwork(MOCK_CHECK_DELAY_MS);


  const question = mockQuiz.questions.find(
    (item) => item.id === questionId
  );

  if (!question) {
    throw new Error("Question not found");
  }

  return {
    correct: selectedIndex === question.correctIndex,
    correctIndex: question.correctIndex,
    explanation: question.explanation,
  };
}



