
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import LessonSection from "./LessonSection";

describe("LessonSection", () => {
  it("displays the lesson heading and body", () => {
    render(
      <LessonSection
        section={{
          heading: "What Is Artificial Intelligence?",
          body: "Artificial Intelligence allows computers to perform tasks that normally require human intelligence.",
        }}
      />
    );

    expect(
      screen.getByRole("heading", {
        name: "What Is Artificial Intelligence?",
      })
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Artificial Intelligence allows computers to perform tasks that normally require human intelligence."
      )
    ).toBeInTheDocument();
  });
});
