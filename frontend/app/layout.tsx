import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MOMUS404 // Hybrid Edge-Cloud QA Orchestrator",
  description:
    "Production-grade autonomous end-to-end web testing platform. Powered by Nous Hermes, Laya 421M edge judge on NVIDIA Quadro P1000, OpenAI self-healing, and Playwright MCP.",
  keywords: ["QA", "automation", "testing", "Playwright", "AI", "edge", "cloud", "momus404"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-white text-black antialiased">{children}</body>
    </html>
  );
}
