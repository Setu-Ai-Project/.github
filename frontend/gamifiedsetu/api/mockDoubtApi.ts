import type { Doubt } from "@/types/doubt";

// Switch to true to simulate backend downtime or errors during testing.
export const MOCK_FORCE_ERROR = false;

// Simulated network round-trip latency in milliseconds.
export const MOCK_DELAY_MS = 400;

// LocalStorage key used to persist the mock doubts list across page refreshes.
export const MOCK_STORAGE_KEY = "setuai_mock_doubts";

// In-memory fallback if localStorage is inaccessible (e.g., SSR, security restrictions).
let memoryStore: Doubt[] = [];

function isLocalStorageAvailable(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const testKey = "__setuai_test__";
    window.localStorage.setItem(testKey, "1");
    window.localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

function getStoredDoubts(): Doubt[] {
  if (!isLocalStorageAvailable()) {
    return [...memoryStore];
  }
  try {
    const raw = window.localStorage.getItem(MOCK_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Doubt[]) : [];
  } catch {
    return [];
  }
}

function saveStoredDoubts(doubts: Doubt[]): void {
  memoryStore = [...doubts];
  if (!isLocalStorageAvailable()) return;
  try {
    window.localStorage.setItem(MOCK_STORAGE_KEY, JSON.stringify(doubts));
  } catch {
    // Gracefully handle storage quota or write errors
  }
}

async function waitAndCheckError(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));
  if (MOCK_FORCE_ERROR) {
    throw new Error("Mock server is down");
  }
}

export async function mockListDoubts(): Promise<Doubt[]> {
  await waitAndCheckError();
  return getStoredDoubts();
}

export async function mockCreateDoubt(
  question: string,
  learnerName: string
): Promise<Doubt> {
  await waitAndCheckError();

  const newDoubt: Doubt = {
    id: crypto.randomUUID(),
    learnerName,
    question,
    status: "open",
    createdAt: new Date().toISOString(),
  };

  const current = getStoredDoubts();
  saveStoredDoubts([newDoubt, ...current]);
  return newDoubt;
}

export async function mockReplyToDoubt(
  id: string,
  text: string,
  mentorName: string
): Promise<Doubt> {
  await waitAndCheckError();

  const current = getStoredDoubts();
  const index = current.findIndex((d) => d.id === id);

  if (index === -1) {
    throw new Error(`Doubt with id ${id} not found`);
  }

  const target = current[index];
  const updatedDoubt: Doubt = {
    ...target,
    status: "answered",
    reply: {
      mentorName,
      text,
      repliedAt: new Date().toISOString(),
    },
  };

  const updatedList = [...current];
  updatedList[index] = updatedDoubt;
  saveStoredDoubts(updatedList);

  return updatedDoubt;
}

export function resetMockDoubts(): void {
  memoryStore = [];
  if (isLocalStorageAvailable()) {
    try {
      window.localStorage.removeItem(MOCK_STORAGE_KEY);
    } catch {
      // Ignore errors when clearing
    }
  }
}
