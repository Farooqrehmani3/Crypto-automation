import type { Metadata } from "next";
import { PortfolioView } from "@/components/portfolio/PortfolioView";

export const metadata: Metadata = {
  title: "Portfolio",
  description: "Track your cryptocurrency portfolio performance with AI-powered analytics.",
};

export default function PortfolioPage() {
  return <PortfolioView />;
}
