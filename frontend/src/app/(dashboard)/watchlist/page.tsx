import type { Metadata } from "next";
import { WatchlistView } from "@/components/watchlist/WatchlistView";

export const metadata: Metadata = {
  title: "Watchlist",
  description: "Track your favorite cryptocurrencies with real-time price updates and alerts.",
};

export default function WatchlistPage() {
  return <WatchlistView />;
}
