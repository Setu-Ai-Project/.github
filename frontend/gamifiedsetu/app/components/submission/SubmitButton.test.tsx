import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SubmitButton from "./SubmitButton";

describe("SubmitButton", () => {
  it("shows an enabled Submit button when not loading", () => {
    render(<SubmitButton onClick={() => {}} loading={false} />);
    expect(screen.getByRole("button", { name: "Submit" })).toBeEnabled();
  });

  it("shows a disabled Checking... button when loading", () => {
    render(<SubmitButton onClick={() => {}} loading={true} />);
    expect(screen.getByRole("button", { name: "Checking..." })).toBeDisabled();
  });

  it("is disabled when the disabled prop is true", () => {
    render(<SubmitButton onClick={() => {}} loading={false} disabled />);
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
  });

  it("calls onClick once when clicked", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<SubmitButton onClick={onClick} loading={false} />);
    await user.click(screen.getByRole("button", { name: "Submit" }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("does not call onClick while loading", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<SubmitButton onClick={onClick} loading={true} />);
    await user.click(screen.getByRole("button", { name: "Checking..." }));
    expect(onClick).not.toHaveBeenCalled();
  });
});