import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Patient Zero — Medical Interview Simulation",
  description:
    "AI-powered standardized patient training. Interview the patient, commit to a clinical impression, and receive structured feedback.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
