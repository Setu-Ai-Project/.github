This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

## Clerk setup

Copy `.env.local.example` to `.env.local` and set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to the publishable key from your Clerk application. The app includes pre-built sign-up and sign-in pages at `/sign-up` and `/sign-in`, and the home page displays the current authentication state.

First, run the development server:

```bash
npm install
npm run dev
```

This project uses **npm only** — don't use `pnpm`, `yarn` or `bun`, and only commit `package-lock.json`.

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Testing with Clerk

Every dev instance has Clerk's **test mode** on by default — no setup needed. Instead of signing up with a real email and checking your inbox for a verification code, use a **test email address** and the fixed test code.

**How it works:**
- Any email with a `+clerk_test` subaddress is treated as a test address — Clerk never actually sends anything to it, and the domain doesn't even need to be real.
- Whatever verification code screen shows up during sign-up/sign-in, enter the fixed code **`424242`**.

**Examples** (swap in your own name so it's clear which account is yours):
```
oliver+clerk_test@example.com
olivernyirongo+clerk_test@example.com
```

This also works with a real provider if you'd rather use one, e.g. `oliver+clerk_test@gmail.com` — Clerk intercepts based on the `+clerk_test` tag before the `@`, so the domain doesn't matter either way, nothing gets delivered.

This doesn't count against Clerk's dev-instance monthly sending limits, so use it freely for local testing.

## Running tests

Tests use [Vitest](https://vitest.dev) and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) in a fake browser (jsdom). Run these from `frontend/gamifiedsetu`:

```bash
npm test             # watch mode: re-runs tests when you save (press q to quit)
npx vitest run       # run every test once
npx vitest run app/components/submission   # run only the tests in one folder (or pass a single file)
```

Before opening a PR, all three checks must pass:

```bash
npx vitest run       # tests
npx tsc --noEmit     # type check (no output = clean)
npm run lint         # lint (0 errors; warnings are OK)
```

**Writing a test:**
- Put it next to the file it tests, named `<Name>.test.ts` or `<Name>.test.tsx` (e.g. `StatusBadge.tsx` → `StatusBadge.test.tsx`).
- `@/` imports work in tests the same as in the app.
- Matchers like `toBeInTheDocument()`, `toBeDisabled()` and `toHaveValue()` are available everywhere.
- `tests/smoke.test.tsx` is the simplest example to copy from.

The setup lives in `vitest.config.mts` (jsdom, `@/` paths, React) and `vitest.setup.ts` (jest-dom matchers, cleanup after each test).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
