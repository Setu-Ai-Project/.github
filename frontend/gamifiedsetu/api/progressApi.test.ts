import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchProgress } from "./progressApi";
import { mockFetchProgress } from "./mockProgress";

vi.mock("./mockProgress", () => ({ mockFetchProgress: vi.fn() }));

const API_URL = "http://api.test";

// Switches to real mode, pointed at a fake API address.
function useRealBackend() {
  vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "");
  vi.stubEnv("NEXT_PUBLIC_API_URL", API_URL);
}

// Makes fetch answer with the given status and JSON body.
function fetchReturns(status: number, body: unknown = {}) {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response);
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  vi.clearAllMocks();
});

describe("fetchProgress in mock mode", () => {
  it("uses the mock and never touches the network or the login token", async () => {
    vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "true");
    vi.stubEnv("NEXT_PUBLIC_API_URL", API_URL);
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const getToken = vi.fn(async () => "tok");

    await fetchProgress(getToken);

    expect(mockFetchProgress).toHaveBeenCalledTimes(1);
    expect(fetchSpy).not.toHaveBeenCalled();
    expect(getToken).not.toHaveBeenCalled();
  });
});

describe("fetchProgress in real mode", () => {
  it("sends the login token and converts the response", async () => {
    useRealBackend();
    const fetchSpy = fetchReturns(200, { total_xp: 260, level: 3, xp_to_next_level: 240 });

    const result = await fetchProgress(async () => "tok");

    expect(fetchSpy).toHaveBeenCalledWith(`${API_URL}/progress/me`, {
      headers: { Authorization: "Bearer tok" },
    });
    expect(result).toEqual({
      totalXp: 260,
      level: 3,
      xpIntoLevel: 10,
      xpForNextLevel: 250,
      skills: [],
    });
  });

  it("maps backend skills to our shape", async () => {
    useRealBackend();
    fetchReturns(200, {
      total_xp: 50,
      skills: [
        {
          id: 4,
          name: "Prompt Lab",
          description: "Write better prompts.",
          module_id: 1,
          status: "locked",
          prerequisites: [1, 2],
          xp_reward: 50,
        },
      ],
    });

    const [skill] = (await fetchProgress()).skills;

    expect(skill).toMatchObject({
      id: "4",
      moduleId: "1",
      prerequisites: ["1", "2"],
      xpReward: 50,
      status: "locked",
    });
  });

  it("sends no Authorization header when there is no token", async () => {
    useRealBackend();
    const fetchSpy = fetchReturns(200, { total_xp: 0 });

    await fetchProgress(async () => null);

    expect(fetchSpy).toHaveBeenCalledWith(`${API_URL}/progress/me`, { headers: {} });
  });

  it("shows zero progress for a learner the backend doesn't know yet (404)", async () => {
    useRealBackend();
    fetchReturns(404);

    const result = await fetchProgress();

    expect(result).toMatchObject({ totalXp: 0, level: 1, skills: [] });
  });

  it("throws a clear error when the backend fails", async () => {
    useRealBackend();
    fetchReturns(500);

    await expect(fetchProgress()).rejects.toThrow("Could not load progress");
  });
});
