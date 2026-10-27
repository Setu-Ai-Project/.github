import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

// The shape every component test follows: render something, then check what's on screen.
describe("test setup", () => {
  it("renders a component and finds its text", () => {
    render(<p>SetuAI tests work</p>);
    expect(screen.getByText("SetuAI tests work")).toBeInTheDocument();
  });
});
