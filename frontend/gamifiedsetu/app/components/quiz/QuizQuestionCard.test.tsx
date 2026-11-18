import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { QuizQuestion } from "@/types/learning";
import QuizQuestionCard from "./QuizQuestionCard";

const QUESTION: QuizQuestion = {
  id: "q1",
  question: "Which of these uses AI?",
  options: ["A calculator", "A photo app that spots faces", "A light switch"],
};

describe("QuizQuestionCard", () => {
  it("shows the question as the group name and one radio per option", () => {
    render(
      <QuizQuestionCard
        question={QUESTION}
        selectedIndex={null}
        onSelect={() => {}}
        isChecked={false}
      />
    );

    expect(screen.getByRole("group", { name: QUESTION.question })).toBeInTheDocument();
    expect(screen.getAllByRole("radio")).toHaveLength(3);
  });

  it("calls onSelect with the option's index when clicked", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <QuizQuestionCard
        question={QUESTION}
        selectedIndex={null}
        onSelect={onSelect}
        isChecked={false}
      />
    );

    await user.click(screen.getByText("A photo app that spots faces"));
    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it("marks the right option and the wrong pick, and locks the radios", () => {
    render(
      <QuizQuestionCard
        question={QUESTION}
        selectedIndex={0}
        onSelect={() => {}}
        isChecked={true}
        correctIndex={1}
      />
    );

    expect(screen.getByText("Correct")).toBeInTheDocument();
    expect(screen.getByText("Not quite")).toBeInTheDocument();
    for (const radio of screen.getAllByRole("radio")) {
      expect(radio).toBeDisabled();
    }
  });

  it("shows only Correct when the pick was right", () => {
    render(
      <QuizQuestionCard
        question={QUESTION}
        selectedIndex={1}
        onSelect={() => {}}
        isChecked={true}
        correctIndex={1}
      />
    );

    expect(screen.getByText("Correct")).toBeInTheDocument();
    expect(screen.queryByText("Not quite")).not.toBeInTheDocument();
  });
});
