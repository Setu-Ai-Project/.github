import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const playerSans = localFont({
  src: [
    {
      path: "./fonts/PlayerSansMono8x13-Classic.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/PlayerSansMono8x13-Bold.ttf",
      weight: "700",
      style: "normal",
    },
    {
      path: "./fonts/PlayerSansMono8x13-Italic.ttf",
      weight: "400",
      style: "italic",
    },
  ],
  variable: "--font-player-sans",
});

export const metadata: Metadata = {
  title: "SetuAI — The Next Step in AI Literacy",
  description: "Sign up or log in to SetuAI, the gamified learning app for kids.",
  icons: { icon: "/setuai-logo.webp" },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${playerSans.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
