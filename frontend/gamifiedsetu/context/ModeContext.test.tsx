import { describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { ModeProvider, useMode } from "./ModeContext";

const wrapper = ({ children }: { children: ReactNode }) => <ModeProvider>{children}</ModeProvider>;

describe("ModeContext", () => {
  it("starts in learner mode", () => {
    const { result } = renderHook(() => useMode(), { wrapper });
    expect(result.current.mode).toBe("learner");
  });

  it("setMode switches the mode", () => {
    const { result } = renderHook(() => useMode(), { wrapper });
    act(() => result.current.setMode("mentor"));
    expect(result.current.mode).toBe("mentor");
  });

  it("can start in a different mode", () => {
    const { result } = renderHook(() => useMode(), {
      wrapper: ({ children }: { children: ReactNode }) => (
        <ModeProvider initialMode="mentor">{children}</ModeProvider>
      ),
    });
    expect(result.current.mode).toBe("mentor");
  });

  it("throws a clear error when used outside ModeProvider", () => {
    // React logs the thrown error to the console; hide that noise for this test.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useMode())).toThrow(
      "useMode must be used inside <ModeProvider>"
    );
    spy.mockRestore();
  });
});
