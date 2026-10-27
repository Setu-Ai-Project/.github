import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-cream px-6 py-12">
      <SignUp
        path="/sign-up"
        routing="path"
        signInUrl="/sign-in"
        fallbackRedirectUrl="/onboarding" // new users take the tour first
        appearance={{
          variables: {
            colorPrimary: "#dc6f51", // coral
            colorForeground: "#172a32", // ink
            colorBackground: "#ffffff",
          },
        }}
      />
    </main>
  );
}
