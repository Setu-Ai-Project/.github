import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import StatusBadge from "./StatusBadge";

describe("StatusBadge", () => {
  it.each([
    ["pending", "Checking...", "bg-cream"],
    ["passed", "Passed!", "bg-tealpop"],
    ["needs_revision", "Needs revision", "bg-coral"],
  ] as const)(
    "shows the right label and colour for %s",
    (status, label, colour) => {
      render(<StatusBadge status={status} />);
      expect(screen.getByText(label)).toHaveClass(colour);
    }
  );
});