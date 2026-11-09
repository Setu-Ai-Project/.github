
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import LearnScreen from "./LearnScreen";
import { getLearnContent } from "@/api/learningApi";

vi.mock("@/api/learningApi", () => ({
  getLearnContent: vi.fn(),
}));

vi.mock("@/app/components/mascots/NovaBanner", () => ({
  default: ({ message }: { message: string }) => <div>{message}</div>,
}));

const mockLesson = {
  id: "1",
  moduleId: "1",
  title: "What Is AI?",
  sections: [
    {
      heading: "Introduction",
      body: "AI helps computers perform tasks that normally require human intelligence.",
    },
    {
      heading: "Examples",
      body: "Voice assistants and recommendation systems use AI.",
    },
  ],
};

describe("LearnScreen", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getLearnContent).mockResolvedValue(mockLesson);
  });

  it("displays the lesson title and first section", async () => {
    render(<LearnScreen moduleId="1" />);

    expect(
      await screen.findByRole("heading", { name: "What Is AI?" })
    ).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: "Introduction" }))
      .toBeInTheDocument();

    expect(screen.getByText("Section 1 of 2")).toBeInTheDocument();
  });

  it("moves to the next section", async () => {
    render(<LearnScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Introduction" });

    fireEvent.click(screen.getByRole("button", { name: "Next section" }));

    expect(
      screen.getByRole("heading", { name: "Examples" })
    ).toBeInTheDocument();

    expect(screen.getByText("Section 2 of 2")).toBeInTheDocument();
  });

  it("moves back to the previous section", async () => {
    render(<LearnScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Introduction" });

    fireEvent.click(screen.getByRole("button", { name: "Next section" }));
    fireEvent.click(screen.getByRole("button", { name: "Previous" }));

    expect(
      screen.getByRole("heading", { name: "Introduction" })
    ).toBeInTheDocument();
  });

  it("shows the quiz link after the final section", async () => {
    render(<LearnScreen moduleId="1" />);

    await screen.findByRole("heading", { name: "Introduction" });

    fireEvent.click(screen.getByRole("button", { name: "Next section" }));

    expect(
      screen.getByRole("link", { name: "Take the quiz" })
    ).toHaveAttribute("href", "/quiz/1");
  });

  it("shows an error message when loading fails", async () => {
    vi.mocked(getLearnContent).mockRejectedValue(
      new Error("Could not load lesson")
    );

    render(<LearnScreen moduleId="1" />);

    expect(await screen.findByRole("alert"))
      .toHaveTextContent("Could not load lesson");
  });
});
