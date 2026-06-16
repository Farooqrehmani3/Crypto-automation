import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { AuthProvider } from "@/providers/AuthProvider";
import { QueryProvider } from "@/providers/QueryProvider";
import { ToastProvider } from "@/providers/ToastProvider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
};

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: {
    default: "TecFlux — AI Crypto Intelligence Platform",
    template: "%s | TecFlux",
  },
  description:
    "AI-powered cryptocurrency analytics platform with real-time market data, predictive forecasting, portfolio management, and multi-agent analysis.",
  keywords: [
    "crypto",
    "cryptocurrency",
    "AI",
    "analytics",
    "predictions",
    "forecasting",
    "portfolio",
    "trading",
    "Bitcoin",
    "Ethereum",
    "market data",
  ],
  authors: [{ name: "TecFlux" }],
  creator: "TecFlux",
  applicationName: "TecFlux",
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "TecFlux",
    title: "TecFlux — AI Crypto Intelligence Platform",
    description:
      "AI-powered cryptocurrency analytics platform with real-time market data and predictive forecasting.",
    images: [{ url: "/images/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "TecFlux — AI Crypto Intelligence Platform",
    description:
      "AI-powered cryptocurrency analytics platform with real-time market data and predictive forecasting.",
    images: ["/images/og-image.png"],
    creator: "@tecflux",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable}`}>
      <body className="font-sans antialiased">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AuthProvider>
            <QueryProvider>
              <ToastProvider />
              {children}
            </QueryProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}