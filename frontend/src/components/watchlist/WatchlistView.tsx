"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Star, TrendingUp, TrendingDown, Search, Plus, Trash2, X, Link2 } from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/shared/EmptyState";
import { PriceBadge } from "@/components/shared/PriceBadge";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { formatCurrency, formatLargeNumber } from "@/lib/utils/formatters";

const COINGECKO_BASE = "https://api.coingecko.com/api/v3";
const DEMO_API_KEY = "CG-fUUVXcpZGgijdkEfJuyU9cU4";

interface WatchlistCoin {
  id: string;
  name: string;
  symbol: string;
  image: string;
}

export function WatchlistView() {
  const [coins, setCoins] = useLocalStorage<WatchlistCoin[]>("watchlist-coins", []);
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [showAdd, setShowAdd] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [loadingPrices, setLoadingPrices] = useState(false);

  // Fetch live prices for all watchlisted coins
  useEffect(() => {
    if (coins.length === 0) return;
    setLoadingPrices(true);
    const ids = coins.map((c) => c.id).join(",");
    fetch(`${COINGECKO_BASE}/coins/markets?vs_currency=usd&ids=${ids}&order=market_cap_desc&sparkline=false&price_change_percentage=24h&x_cg_demo_api_key=${DEMO_API_KEY}`)
      .then((r) => r.json())
      .then((data) => {
        const map: Record<string, any> = {};
        for (const d of data) map[d.id] = d;
        setPrices(map);
      })
      .catch(() => {})
      .finally(() => setLoadingPrices(false));
  }, [coins]);

  // Search coins for adding
  const searchCoins = async (query: string) => {
    if (query.length < 2) { setSearchResults([]); return; }
    setSearching(true);
    try {
      const res = await fetch(`${COINGECKO_BASE}/search?query=${encodeURIComponent(query)}&x_cg_demo_api_key=${DEMO_API_KEY}`);
      const data = await res.json();
      // Filter out already-watchlisted coins
      const existing = new Set(coins.map((c) => c.id));
      setSearchResults((data.coins || []).filter((c: any) => !existing.has(c.id)).slice(0, 10));
    } catch { setSearchResults([]); }
    finally { setSearching(false); }
  };

  const addCoin = (coin: any) => {
    setCoins([...coins, {
      id: coin.id,
      name: coin.name,
      symbol: coin.symbol?.toUpperCase() || coin.id.toUpperCase(),
      image: coin.thumb || coin.large || "",
    }]);
    setSearchResults([]);
    setSearchQuery("");
    setShowAdd(false);
  };

  const removeCoin = (id: string) => {
    setCoins(coins.filter((c) => c.id !== id));
  };

  // Filter by local search
  const localQuery = searchQuery.toLowerCase();
  const filtered = coins.filter((c) =>
    !localQuery || c.name.toLowerCase().includes(localQuery) || c.symbol.toLowerCase().includes(localQuery)
  );

  if (coins.length === 0 && !showAdd) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <EmptyState
          icon={Star}
          title="Your watchlist is empty"
          description="Track your favorite cryptocurrencies. Get live prices and quick access to AI analysis."
          action={{
            label: "Add Coins",
            onClick: () => setShowAdd(true),
            icon: Plus,
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white sm:text-3xl">Watchlist</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {coins.length} coin{coins.length !== 1 ? "s" : ""} tracked
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Input
            placeholder="Filter watchlist..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48 sm:w-64"
          />
          <Button size="sm" className="gap-2 shrink-0" onClick={() => setShowAdd(!showAdd)}>
            {showAdd ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showAdd ? "Cancel" : "Add Coin"}
          </Button>
        </div>
      </div>

      {/* Add Coin Panel */}
      {showAdd && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Search coins to add</h3>
            <Input
              placeholder="Search by name or symbol..."
              onChange={(e) => searchCoins(e.target.value)}
              autoFocus
            />
            <div className="mt-2 space-y-1 max-h-64 overflow-y-auto">
              {searchResults.map((coin: any) => (
                <button
                  key={coin.id}
                  onClick={() => addCoin(coin)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-left transition-colors"
                >
                  {coin.thumb && <img src={coin.thumb} alt="" className="w-6 h-6 rounded-full" />}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                    <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                  </div>
                  <Plus className="h-4 w-4 text-slate-400" />
                </button>
              ))}
              {!searching && searchResults.length === 0 && (
                <p className="text-xs text-slate-400 text-center py-3">Type at least 2 characters to search</p>
              )}
              {searching && <p className="text-xs text-slate-400 text-center py-3">Searching...</p>}
            </div>
          </Card>
        </motion.div>
      )}

      {/* Watchlist Table */}
      {coins.length > 0 && (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800">
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Asset</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">24h Change</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase hidden md:table-cell">Market Cap</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase w-16"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((coin) => {
                  const p = prices[coin.id];
                  const currentPrice = p?.current_price;
                  const change24h = p?.price_change_percentage_24h;
                  const marketCap = p?.market_cap;

                  return (
                    <tr key={coin.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <Link href={`/coins/${coin.id}`} className="flex items-center gap-3 hover:opacity-80">
                          {coin.image ? (
                            <img src={coin.image} alt="" className="w-8 h-8 rounded-full" />
                          ) : (
                            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                              {coin.symbol.charAt(0)}
                            </div>
                          )}
                          <div>
                            <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                            <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                          </div>
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-slate-900 dark:text-white tabular-nums">
                        {currentPrice ? formatCurrency(currentPrice) : (loadingPrices ? "..." : "—")}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {change24h != null ? <PriceBadge value={change24h} showIcon size="sm" /> : (loadingPrices ? "..." : "—")}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-slate-500 hidden md:table-cell tabular-nums">
                        {marketCap ? formatLargeNumber(marketCap) : (loadingPrices ? "..." : "—")}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => removeCoin(coin.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/50 transition-colors"
                          title="Remove from watchlist"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
