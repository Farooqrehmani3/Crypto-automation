import type { Metadata } from "next";
import { CoinDetailView } from "@/components/coins/CoinDetailView";

interface CoinPageProps {
  params: Promise<{ coinId: string }>;
}

export async function generateMetadata({ params }: CoinPageProps): Promise<Metadata> {
  const { coinId } = await params;
  const name = coinId.charAt(0).toUpperCase() + coinId.slice(1).replace(/-/g, " ");

  return {
    title: `${name} Analysis`,
    description: `AI-powered analysis and real-time data for ${name}. Technical, sentiment, fundamental, and on-chain insights.`,
  };
}

export default async function CoinPage({ params }: CoinPageProps) {
  const { coinId } = await params;

  return <CoinDetailView coinId={coinId} />;
}
