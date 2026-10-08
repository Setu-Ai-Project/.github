import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import FeedbackList from "./FeedbackList";

describe("FeedbackList", () => {
  it("shows one list item per tip, in order", () => {
    render(<FeedbackList items={["First tip", "Second tip"]} />);
    const listItems = screen.getAllByRole("listitem");
    expect(listItems).toHaveLength(2);
    expect(listItems[0]).toHaveTextContent("First tip");
    expect(listItems[1]).toHaveTextContent("Second tip");
  });

  it("renders nothing when there are no tips", () => {
    const { container } = render(<FeedbackList items={[]} />);
    expect(container).toBeEmptyDOMElement();
  });
});