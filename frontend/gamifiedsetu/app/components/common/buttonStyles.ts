export type ButtonVariant = "teal" | "white" | "coral";

// The shared SetuAI button look: thick ink border, hard shadow, small lift on hover,
// faded with a not-allowed cursor when disabled.
const BASE_CLASSES =
  "inline-block rounded-2xl border-4 border-ink px-6 py-3 text-center font-display font-bold text-ink shadow-[4px_4px_0_#172A32] transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0";

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  teal: "bg-tealpop",
  white: "bg-white",
  coral: "bg-coral",
};

// Class names for a button or a link that should look like a button.
export function buttonClass(variant: ButtonVariant): string {
  return `${BASE_CLASSES} ${VARIANT_CLASSES[variant]}`;
}
