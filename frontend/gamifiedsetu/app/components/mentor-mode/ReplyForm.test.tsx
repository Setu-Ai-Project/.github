import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ReplyForm from "./ReplyForm";

const LABEL = "Reply to: What is a variable?";

describe("ReplyForm", () => {
  it("keeps Send reply disabled until real text is typed", async () => {
    const user = userEvent.setup();
    render(<ReplyForm replyTo="What is a variable?" onSend={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Send reply" })).toBeDisabled();
    await user.type(screen.getByLabelText(LABEL), "   ");
    expect(screen.getByRole("button", { name: "Send reply" })).toBeDisabled();
  });

  it("sends the trimmed reply and clears the box", async () => {
    const onSend = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<ReplyForm replyTo="What is a variable?" onSend={onSend} />);

    await user.type(screen.getByLabelText(LABEL), "  A named box for a value.  ");
    await user.click(screen.getByRole("button", { name: "Send reply" }));

    expect(onSend).toHaveBeenCalledWith("A named box for a value.");
    expect(screen.getByLabelText(LABEL)).toHaveValue("");
  });

  it("shows a friendly error and keeps the text when sending fails", async () => {
    const onSend = vi.fn().mockRejectedValue(new Error("boom"));
    const user = userEvent.setup();
    render(<ReplyForm replyTo="What is a variable?" onSend={onSend} />);

    await user.type(screen.getByLabelText(LABEL), "A named box.");
    await user.click(screen.getByRole("button", { name: "Send reply" }));

    expect(
      await screen.findByText("We could not send your reply. Please try again.")
    ).toBeInTheDocument();
    expect(screen.getByLabelText(LABEL)).toHaveValue("A named box.");
  });

  it('shows "Sending..." and only sends once when clicked twice', async () => {
    const onSend = vi.fn().mockReturnValue(new Promise(() => {})); // never finishes
    const user = userEvent.setup();
    render(<ReplyForm replyTo="What is a variable?" onSend={onSend} />);

    await user.type(screen.getByLabelText(LABEL), "A named box.");
    await user.click(screen.getByRole("button", { name: "Send reply" }));
    await user.click(screen.getByRole("button", { name: "Sending..." }));

    expect(screen.getByRole("button", { name: "Sending..." })).toBeDisabled();
    expect(onSend).toHaveBeenCalledTimes(1);
  });
});
