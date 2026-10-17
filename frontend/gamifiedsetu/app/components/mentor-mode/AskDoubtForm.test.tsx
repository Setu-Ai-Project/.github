import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AskDoubtForm, { TEST_LEARNER_NAME } from "./AskDoubtForm";
import { createDoubt } from "@/api/doubtApi";

vi.mock("@/api/doubtApi", () => ({
  createDoubt: vi.fn(),
  listDoubts: vi.fn(),
}));

describe("AskDoubtForm", () => {
  const onSent = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a validation message for a question that is too short", async () => {
    const user = userEvent.setup();

    render(<AskDoubtForm onSent={onSent} />);

    await user.type(screen.getByLabelText("Ask a doubt"), "Hey");
    await user.click(screen.getByRole("button", { name: "Send doubt" }));

    expect(
      screen.getByText("Please describe your doubt in a few words."),
    ).toBeInTheDocument();
    expect(createDoubt).not.toHaveBeenCalled();
    expect(onSent).not.toHaveBeenCalled();
  });

  it("sends a trimmed question, clears the form, and notifies the parent", async () => {
    const user = userEvent.setup();
    vi.mocked(createDoubt).mockResolvedValue({
      id: "doubt-1",
      learnerName: TEST_LEARNER_NAME,
      question: "How do I solve this?",
      status: "open",
      createdAt: "2026-10-13T08:00:00.000Z",
    });

    render(<AskDoubtForm onSent={onSent} />);

    const textarea = screen.getByLabelText("Ask a doubt");
    await user.type(textarea, "  How do I solve this?  ");
    await user.click(screen.getByRole("button", { name: "Send doubt" }));

    await waitFor(() => {
      expect(createDoubt).toHaveBeenCalledWith(
        "How do I solve this?",
        TEST_LEARNER_NAME,
      );
    });

    expect(
      await screen.findByText("Doubt sent! A mentor will reply soon."),
    ).toBeInTheDocument();
    expect(textarea).toHaveValue("");
    expect(onSent).toHaveBeenCalledTimes(1);
  });

  it("keeps the question and shows an error if sending fails", async () => {
    const user = userEvent.setup();
    vi.mocked(createDoubt).mockRejectedValue(new Error("Network error"));

    render(<AskDoubtForm onSent={onSent} />);

    const textarea = screen.getByLabelText("Ask a doubt");
    await user.type(textarea, "I need help with this topic");
    await user.click(screen.getByRole("button", { name: "Send doubt" }));

    expect(
      await screen.findByText(
        "We could not send your doubt. Please try again.",
      ),
    ).toBeInTheDocument();
    expect(textarea).toHaveValue("I need help with this topic");
    expect(onSent).not.toHaveBeenCalled();
  });

  it("prevents duplicate submissions while a request is pending", async () => {
    const user = userEvent.setup();
    let finishRequest: (value: {
      id: string;
      learnerName: string;
      question: string;
      status: "open";
      createdAt: string;
    }) => void = () => {};

    vi.mocked(createDoubt).mockImplementation(
      () =>
        new Promise((resolve) => {
          finishRequest = resolve as typeof finishRequest;
        }),
    );

    render(<AskDoubtForm onSent={onSent} />);

    await user.type(screen.getByLabelText("Ask a doubt"), "Please explain this");
    await user.click(screen.getByRole("button", { name: "Send doubt" }));

    expect(
      await screen.findByRole("button", { name: "Sending..." }),
    ).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "Sending..." }));

    expect(createDoubt).toHaveBeenCalledTimes(1);

    finishRequest({
      id: "doubt-2",
      learnerName: TEST_LEARNER_NAME,
      question: "Please explain this",
      status: "open",
      createdAt: "2026-10-13T08:00:00.000Z",
    });

    await waitFor(() => {
      expect(onSent).toHaveBeenCalledTimes(1);
    });
  });
});
