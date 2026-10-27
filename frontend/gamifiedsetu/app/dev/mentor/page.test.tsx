import { beforeEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { resetMockDoubts } from "@/api/mockDoubtApi";
import MentorModePage from "./page";

// Each step waits on the 400ms mock, so give findBy* longer than its 1s default.
const WAIT = { timeout: 3000 };
const QUESTION = "How do I stop an infinite loop?";
const REPLY = "Make sure the loop condition eventually becomes false.";

describe("Mentor Mode page: full journey", () => {
  beforeEach(() => resetMockDoubts());

  it("learner asks → mentor replies → learner sees the reply", async () => {
    const user = userEvent.setup();
    render(<MentorModePage />);

    // 1. Learner sends a doubt
    await user.type(screen.getByLabelText("Ask a doubt"), QUESTION);
    await user.click(screen.getByRole("button", { name: "Send doubt" }));
    expect(await screen.findByText("Doubt sent! A mentor will reply soon.", {}, WAIT)).toBeInTheDocument();
    expect(await screen.findByText("Open", {}, WAIT)).toBeInTheDocument();

    // 2. Mentor sees it in Open (1) and replies
    await user.click(screen.getByRole("button", { name: "Mentor" }));
    expect(await screen.findByRole("button", { name: "Open (1)" }, WAIT)).toBeInTheDocument();
    await user.type(screen.getByLabelText(`Reply to: ${QUESTION}`), REPLY);
    await user.click(screen.getByRole("button", { name: "Send reply" }));
    expect(await screen.findByRole("button", { name: "Answered (1)" }, WAIT)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open (0)" })).toBeInTheDocument();

    // 3. Learner sees the doubt answered, with the reply
    await user.click(screen.getByRole("button", { name: "Learner" }));
    expect(await screen.findByText("Test Mentor says:", {}, WAIT)).toBeInTheDocument();
    expect(screen.getByText(REPLY)).toBeInTheDocument();
    expect(screen.getByText("Answered")).toBeInTheDocument();
  }, 15000);
});
