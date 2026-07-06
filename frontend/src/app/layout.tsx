import type { Metadata } from "next";
import NetworkBackground from "@/components/NetworkBackground";
import "./globals.css";

export const metadata: Metadata = {
  title: "AntiRAGing — Codebase Onboarding Agent",
  description: "Paste a GitHub URL. Get a structured, queryable onboarding guide for any codebase in minutes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <NetworkBackground />
        {children}
      </body>
    </html>
  );
}
