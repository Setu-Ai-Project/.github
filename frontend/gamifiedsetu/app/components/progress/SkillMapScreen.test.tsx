import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";

import { getMockProgress } from "@/api/mockProgress";
import { useProgressPolling } from "@/hooks/useProgressPolling";
import SkillMapScreen from "./SkillMapScreen";

vi.mock("@/hooks/useProgressPolling", () => ({
  useProgressPolling: vi.fn(),
  DEFAULT_POLL_MS: 5000,
}));

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

vi.mock("@/app/components/progress/DevSimulator", () => ({
  default: () => null,
}));

const mockedUseProgressPolling = vi.mocked(useProgressPolling);
const mockedUseRouter = vi.mocked(useRouter);

describe("SkillMapScreen", () => {
  const push = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseRouter.mockReturnValue({
      push,
    } as unknown as ReturnType<typeof useRouter>);
  });

  it("shows loading status message when loading with no data", () => {
    mockedUseProgressPolling.mockReturnValue({
      data: null,
      error: null,
      loading: true,
    });

    render(<SkillMapScreen />);

    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(
      screen.getByText("Getting your skill map ready...")
    ).toBeInTheDocument();
  });

  it("shows error alert with retry button when error occurs with no data, and retrying increments refreshKey", async () => {
    const user = userEvent.setup();
    mockedUseProgressPolling.mockReturnValue({
      data: null,
      error: new Error("Failed to load"),
      loading: false,
    });

    render(<SkillMapScreen />);

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(
      screen.getByText("We could not load your skill map.")
    ).toBeInTheDocument();

    const tryAgainButton = screen.getByRole("button", { name: "Try again" });
    await user.click(tryAgainButton);

    expect(mockedUseProgressPolling).toHaveBeenLastCalledWith(5000, 1);
  });

  it("renders the skill map with headings and routes to module on skill click", async () => {
    const user = userEvent.setup();
    const snapshot = getMockProgress();
    mockedUseProgressPolling.mockReturnValue({
      data: snapshot,
      error: null,
      loading: false,
    });

    render(<SkillMapScreen />);

    expect(
      screen.getByRole("heading", { name: "Skill Map", level: 1 })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Tier 1", level: 2 })
    ).toBeInTheDocument();

    const skillButton = screen.getByRole("button", {
      name: "Skill: Swipe-Sort: AI or Not AI?, Complete",
    });
    await user.click(skillButton);

    expect(push).toHaveBeenCalledWith("/module/1");
  });

  it("renders both the map and the warning notice when error occurs with existing data", () => {
    const snapshot = getMockProgress();
    mockedUseProgressPolling.mockReturnValue({
      data: snapshot,
      error: new Error("Network down"),
      loading: false,
    });

    render(<SkillMapScreen />);

    expect(
      screen.getByText("Having trouble updating. Showing your last progress.")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Tier 1", level: 2 })
    ).toBeInTheDocument();
  });
});
