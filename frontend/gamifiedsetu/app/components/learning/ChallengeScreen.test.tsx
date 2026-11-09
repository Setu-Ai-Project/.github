
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { getBuilderChallenge } from "@/api/learningApi";
import ChallengeScreen from "./ChallengeScreen";

vi.mock("@/api/learningApi", () => ({
  getBuilderChallenge: vi.fn(),
}));

const mockChallenge = {
  id: "challenge-1",
  moduleId: "1",
  title: "Describe a sunset",
  goal: "Create a description of a sunset.",
  instructions: "Think about the colours and the atmosphere.",
  hints: [
    "Think about the colours in the sky.",
    "Consider how the sun disappears below the horizon.",
  ],
};

describe("ChallengeScreen", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getBuilderChallenge).mockResolvedValue(mockChallenge);
  });

  it("displays the challenge title, goal and instructions", async () => {
    render(<ChallengeScreen moduleId="1" />);

    expect(
      await screen.findByRole("heading", {
        name: "Describe a sunset",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText("Create a description of a sunset.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Think about the colours and the atmosphere.")
    ).toBeInTheDocument();
  });

  it("displays the challenge tip", async () => {
    render(<ChallengeScreen moduleId="1" />);

    expect(
      await screen.findByText("Tip: start small, test often.")
    ).toBeInTheDocument();
  });

  it("reveals hints when requested", async () => {
    render(<ChallengeScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Describe a sunset" });

    expect(
      screen.getByText("0 of 2 hints shown")
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: "Show next hint" })
    );

    expect(
      screen.getByText("Think about the colours in the sky.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("1 of 2 hints shown")
    ).toBeInTheDocument();
  });

  it("displays the submission panel", async () => {
    render(<ChallengeScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Describe a sunset" });

    expect(
      screen.getByRole("heading", { name: "Your work" })
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText("Your answer")
    ).toBeInTheDocument();
  });

  it("provides a link back to the module", async () => {
    render(<ChallengeScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Describe a sunset" });

    expect(
      screen.getByRole("link", { name: "Back to module" })
    ).toHaveAttribute("href", "/module/1");
  });

  it("shows an error when the challenge fails to load", async () => {
    vi.mocked(getBuilderChallenge).mockRejectedValue(
      new Error("Could not load challenge")
    );

    render(<ChallengeScreen moduleId="1" />);

    expect(await screen.findByRole("alert"))
      .toHaveTextContent("Could not load challenge");
  });
});
