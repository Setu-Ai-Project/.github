import { shouldUseMock } from "./mockHelpers";

export interface BugMistake {
  id: string;
  matched: string;
  explanation: string;
  fixHint: string;
}

export interface ModerationResult {
  isSafe: boolean;
  reason?: string | null;
}

// Fallback client-side mock check for Bug mistakes when mock mode is enabled
function mockCheckMistakes(text: string): BugMistake[] {
  const lowered = text.toLowerCase();
  const found: BugMistake[] = [];

  if (lowered.includes("something nice") || lowered.includes("something cool")) {
    found.push({
      id: "m1-vague-words",
      matched: "something nice",
      explanation: "AI models cannot guess what 'nice' means to you.",
      fixHint: "Name specific colors, textures, or lighting instead.",
    });
  }

  return found;
}

export async function checkBugMistakes(
  text: string,
  moduleId: string = "default"
): Promise<BugMistake[]> {
  if (shouldUseMock()) {
    return mockCheckMistakes(text);
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    return mockCheckMistakes(text);
  }

  try {
    const res = await fetch(`${apiUrl}/bug-triggers/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, module_id: moduleId }),
    });

    if (!res.ok) {
      return mockCheckMistakes(text);
    }

    const data = await res.json();
    return (data || []).map((item: any) => ({
      id: item.id,
      matched: item.matched,
      explanation: item.explanation,
      fixHint: item.fix_hint || item.fixHint || "",
    }));
  } catch (err) {
    return mockCheckMistakes(text);
  }
}

export async function checkContentModeration(
  text: string
): Promise<ModerationResult> {
  if (shouldUseMock()) {
    const lowered = text.toLowerCase();
    const unsafe = ["bomb", "weapon", "blood", "kill"].some((w) =>
      lowered.includes(w)
    );
    return {
      isSafe: !unsafe,
      reason: unsafe ? "Let's keep our prompts friendly and safe!" : null,
    };
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    return { isSafe: true };
  }

  try {
    const res = await fetch(`${apiUrl}/ai/moderate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      return { isSafe: true };
    }

    const data = await res.json();
    return {
      isSafe: data.is_safe,
      reason: data.reason,
    };
  } catch {
    return { isSafe: true };
  }
}
