// Shared helpers for the fake backends in api/, so each mock file
// doesn't need its own copy.

// Mock or real backend? Reads the env WHEN CALLED (not at the top of the file),
// so tests can change it. Same rule as api/learningApi.ts.
export function shouldUseMock(): boolean {
  return (
    process.env.NEXT_PUBLIC_USE_MOCK === "true" ||
    !process.env.NEXT_PUBLIC_API_URL
  );
}

// Pretends to be the network: waits `delayMs`, then fails if `forceError` is true.
export async function fakeNetwork(delayMs: number, forceError: boolean): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, delayMs));

  if (forceError) {
    throw new Error("Mock server is down");
  }
}
