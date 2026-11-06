import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import LoadingState from "./LoadingState";

describe("LoadingState", () => {
  it("displays the default loading message", () => {
    render(<LoadingState />);

    expect(
      screen.getByText("Getting things ready...")
    ).toBeInTheDocument();
  });

  it("displays a custom loading message", () => {
    render(<LoadingState message="Loading your lesson..." />);

    expect(
      screen.getByText("Loading your lesson...")
    ).toBeInTheDocument();
  });
});