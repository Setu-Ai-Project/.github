import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import DoubtCard from "./DoubtCard";
import type { Doubt } from "@/types/doubt";

describe("DoubtCard", () => {
  it("renders open status, question, bg-cream badge, and waiting message", () => {
    const openDoubt: Doubt = {
      id: "doubt-1",
      learnerName: "Aarav",
      question: "How do I exit a while loop?",
      status: "open",
      createdAt: "2026-10-12T10:00:00Z",
    };

    render(<DoubtCard doubt={openDoubt} />);

    // Question
    expect(screen.getByText("How do I exit a while loop?")).toBeInTheDocument();

    // Badge
    const badge = screen.getByText("Open");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-cream");

    // Waiting message
    expect(
      screen.getByText("Waiting for a mentor to reply...")
    ).toBeInTheDocument();

    // No mentor reply content
    expect(screen.queryByText(/says:/)).not.toBeInTheDocument();
  });

  it("renders answered status, bg-tealpop badge, mentor label and reply text, and no waiting message", () => {
    const answeredDoubt: Doubt = {
      id: "doubt-2",
      learnerName: "Zoya",
      question: "What is CSS Grid?",
      status: "answered",
      createdAt: "2026-10-12T10:00:00Z",
      reply: {
        mentorName: "Mentor Priya",
        text: "CSS Grid is a 2D layout system for web pages.",
        repliedAt: "2026-10-12T10:30:00Z",
      },
    };

    render(<DoubtCard doubt={answeredDoubt} />);

    // Question
    expect(screen.getByText("What is CSS Grid?")).toBeInTheDocument();

    // Badge
    const badge = screen.getByText("Answered");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-tealpop");

    // Mentor response
    expect(screen.getByText("Mentor Priya says:")).toBeInTheDocument();
    expect(
      screen.getByText("CSS Grid is a 2D layout system for web pages.")
    ).toBeInTheDocument();

    // No waiting message
    expect(
      screen.queryByText("Waiting for a mentor to reply...")
    ).not.toBeInTheDocument();
  });

  it("renders learner attribution correctly", () => {
    const doubt: Doubt = {
      id: "doubt-3",
      learnerName: "Rohan",
      question: "What is a component?",
      status: "open",
      createdAt: "2026-10-12T10:00:00Z",
    };

    render(<DoubtCard doubt={doubt} />);

    expect(screen.getByText("Asked by Rohan")).toBeInTheDocument();
  });
});
