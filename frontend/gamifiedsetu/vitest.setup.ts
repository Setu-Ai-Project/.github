// Adds readable matchers like toBeInTheDocument(), toBeDisabled(), toHaveValue().
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// Remove whatever a test rendered before the next test starts.
afterEach(() => cleanup());
