
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createDoubt, listDoubts } from "@/api/doubtApi";
import type { Doubt } from "@/types/doubt";
import MyDoubts from "./MyDoubts";

vi.mock("@/api/doubtApi", () => ({
  listDoubts: vi.fn(),
  createDoubt: vi.fn(),
}));

const mockedListDoubts = vi.mocked(listDoubts);
const mockedCreateDoubt = vi.mocked(createDoubt);

const olderDoubt: Doubt = {
  id: "1",
  learnerName: "Test Learner",
  question: "How do variables work?",
  status: "answered",
  createdAt: "2026-10-10T09:00:00.000Z",
  reply: {
    mentorName: "Test Mentor",
    text: "A variable stores a value.",
    repliedAt: "2026-10-10T10:00:00.000Z",
  },
};

const newerDoubt: Doubt = {
  id: "2",
  learnerName: "Test Learner",
  question: "How do functions work?",
  status: "open",
  createdAt: "2026-10-12T09:00:00.000Z",
};

beforeEach(() => {
  vi.clearAllMocks();
  mockedListDoubts.mockResolvedValue([]);
});

describe("MyDoubts", () => {
  it("shows the empty state when there are no doubts", async () => {
    render(<MyDoubts />);

    expect(
      await screen.findByText(
        "No doubts yet. Ask your first one above!"
      )
    ).toBeInTheDocument();
  });

  it("shows doubts newest first and displays mentor replies", async () => {
    mockedListDoubts.mockResolvedValue([
      olderDoubt,
      newerDoubt,
    ]);

    render(<MyDoubts />);

    const newerQuestion = await screen.findByText(
      "How do functions work?"
    );
    const olderQuestion = screen.getByText(
      "How do variables work?"
    );

    const cards = screen.getAllByRole("article");

    expect(cards).toHaveLength(2);
    expect(
      within(cards[0]).getByText("How do functions work?")
    ).toBe(newerQuestion);
    expect(
      within(cards[1]).getByText("How do variables work?")
    ).toBe(olderQuestion);

    expect(
      screen.getByText("A variable stores a value.")
    ).toBeInTheDocument();
  });

  it("shows an error when loading doubts fails", async () => {
    mockedListDoubts.mockRejectedValueOnce(
      new Error("Loading failed")
    );

    render(<MyDoubts />);

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent(
      "We could not load your doubts. Please refresh the page."
    );
  });

  it("reloads the list after a new doubt is submitted", async () => {
    const user = userEvent.setup();

    mockedListDoubts
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([newerDoubt]);

    mockedCreateDoubt.mockResolvedValue(newerDoubt);

    render(<MyDoubts />);

    expect(
      await screen.findByText(
        "No doubts yet. Ask your first one above!"
      )
    ).toBeInTheDocument();

    await user.type(
      screen.getByRole("textbox", { name: "Ask a doubt" }),
      "How do functions work?"
    );

    await user.click(
      screen.getByRole("button", { name: "Send doubt" })
    );

    expect(
      await screen.findByText("How do functions work?")
    ).toBeInTheDocument();

    expect(mockedListDoubts).toHaveBeenCalledTimes(2);
  });
});
