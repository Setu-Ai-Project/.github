import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  // tsconfigPaths makes "@/..." imports work inside tests, exactly like in the app.
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: "jsdom", // a fake browser so components can render in tests
    setupFiles: ["./vitest.setup.ts"],
  },
});
