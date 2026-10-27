import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { listDoubts, replyToDoubt } from "@/api/doubtApi";
import type { Doubt } from "@/types/doubt";
import MentorDashboard from "./MentorDashboard";

vi.mock("@/api/doubtApi", () => ({ listDoubts: vi.fn(), replyToDoubt: vi.fn() }));
const mockedList = vi.mocked(listDoubts);
const mockedReply = vi.mocked(replyToDoubt);

function makeDoubt(id: string, question: string, createdAt: string): Doubt {
  return { id, learnerName: "Test Learner", question, status: "open", createdAt };
}

const NEWER_OPEN = makeDoubt("2", "Newer question", "2026-10-02T12:00:00.000Z");
const OLDER_OPEN = makeDoubt("1", "Older question", "2026-10-02T09:00:00.000Z");
const ANSWERED: Doubt = {
  ...makeDoubt("3", "Answered question", "2026-10-01T09:00:00.000Z"),
  status: "answered",
  reply: { mentorName: "Test Mentor", text: "Already answered.", repliedAt: "2026-10-01T10:00:00.000Z" },
};

describe("MentorDashboard", () => {
  beforeEach(() => {
    mockedList.mockReset();
    mockedReply.mockReset();
  });

  it("shows tab counts and open doubts oldest first", async () => {
    mockedList.mockResolvedValue([NEWER_OPEN, ANSWERED, OLDER_OPEN]);
    render(<MentorDashboard />);

    expect(await screen.findByRole("button", { name: "Open (2)" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Answered (1)" })).toBeInTheDocument();

    const cards = screen.getAllByRole("article");
    expect(cards[0]).toHaveTextContent("Older question");
    expect(cards[1]).toHaveTextContent("Newer question");
  });

  it("shows answered doubts with their reply and no reply box on the Answered tab", async () => {
    mockedList.mockResolvedValue([OLDER_OPEN, ANSWERED]);
    const user = userEvent.setup();
    render(<MentorDashboard />);

    await user.click(await screen.findByRole("button", { name: "Answered (1)" }));
    expect(screen.getByText("Already answered.")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("sends a reply as Test Mentor and moves the doubt to Answered", async () => {
    const answered: Doubt = {
      ...OLDER_OPEN,
      status: "answered",
      reply: { mentorName: "Test Mentor", text: "Use break.", repliedAt: "2026-10-02T10:00:00.000Z" },
    };
    mockedList.mockResolvedValueOnce([OLDER_OPEN]).mockResolvedValue([answered]);
    mockedReply.mockResolvedValue(answered);
    const user = userEvent.setup();
    render(<MentorDashboard />);

    await user.type(await screen.findByLabelText("Reply to: Older question"), "Use break.");
    await user.click(screen.getByRole("button", { name: "Send reply" }));

    expect(mockedReply).toHaveBeenCalledWith("1", "Use break.", "Test Mentor");
    expect(await screen.findByRole("button", { name: "Answered (1)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open (0)" })).toBeInTheDocument();
    expect(screen.getByText("Nothing here yet.")).toBeInTheDocument();
  });

  it("shows a friendly message when the queue is empty", async () => {
    mockedList.mockResolvedValue([]);
    render(<MentorDashboard />);
    expect(await screen.findByText("Nothing here yet.")).toBeInTheDocument();
  });

  it("shows a friendly error instead of a blank screen when loading fails", async () => {
    mockedList.mockRejectedValue(new Error("boom"));
    render(<MentorDashboard />);
    expect(
      await screen.findByText("We could not load the doubts. Please refresh the page.")
    ).toBeInTheDocument();
  });

  it("shows the reply error when sending a reply fails", async () => {
    mockedList.mockResolvedValue([OLDER_OPEN]);
    mockedReply.mockRejectedValue(new Error("boom"));
    const user = userEvent.setup();
    render(<MentorDashboard />);

    await user.type(await screen.findByLabelText("Reply to: Older question"), "Use break.");
    await user.click(screen.getByRole("button", { name: "Send reply" }));

    expect(await screen.findByText("We could not send your reply. Please try again.")).toBeInTheDocument();
  });
});
