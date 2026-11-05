import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import ScreenShell from "./ScreenShell";

describe("ScreenShell", () => {
  it("displays its label and children", () => {
    render(
      <ScreenShell label="Learning">
        <h1>Learning Dashboard</h1>
      </ScreenShell>
    );

    expect(screen.getByText("Learning")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Learning Dashboard" })
    ).toBeInTheDocument();
  });

  it("displays a back link when backHref is provided", () => {
    render(
      <ScreenShell
        label="Dev"
        backHref="/dashboard"
        backLabel="Back to dashboard"
      >
        <p>Test content</p>
      </ScreenShell>
    );

    const backLink = screen.getByRole("link", {
      name: "← Back to dashboard",
    });

    expect(backLink).toBeInTheDocument();
    expect(backLink).toHaveAttribute("href", "/dashboard");
  });

  it("does not display a back link when backHref is not provided", () => {
    render(
      <ScreenShell label="Learning">
        <p>Test content</p>
      </ScreenShell>
    );

    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  it("uses Back as the default back label", () => {
    render(
      <ScreenShell label="Dev" backHref="/dashboard">
        <p>Test content</p>
      </ScreenShell>
    );

    expect(
      screen.getByRole("link", { name: "← Back" })
    ).toBeInTheDocument();
  });
});