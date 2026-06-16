"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  Sparkles,
  Coins,
  Gauge,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KPICard, KPIGrid } from "@/components/dashboard/KPICard";
import { CardSkeleton, ChartSkeleton } from "@/components/ui/skeleton";
import { fetchTopCoins, fetchGlobalData, fetchFearGreedIndex } from "@/lib/api/coingecko-direct";
import { formatCurrency, formatLargeNumber, formatPercentage } from "@/lib/utils/formatters";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export function DashboardView() {
  // Fetch top 20 coins
  const { data: coins, isLoading: coinsLoading } = useQuery({
    queryKey: ["topCoins"],
    queryFn: () => fetchTopCoins(20),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  // Fetch global market data
  const { data: globalData, isLoading: globalLoading } = useQuery({
    queryKey: ["globalData"],
    queryFn: fetchGlobalData,
    staleTime: 60_000,
    refetchInterval: 120_000,
  });

  // Fetch Fear & Greed Index
  const { data: fearGreed } = useQuery({
    queryKey: ["fearGreed"],
    queryFn: fetchFearGreedIndex,
    staleTime: 300_000,
    refetchInterval: 600_000,
  });

  const isLoading = coinsLoading || globalLoading;

  // Compute stats from live data
  const globalStats = globalData?.data;
  const marketCap = globalStats?.total_market_cap?.usd ?? 0;
  const totalVolume = globalStats?.total_volume?.usd ?? 0;
  const btcDominance = globalStats?.market_cap_percentage?.btc ?? 0;
  const marketCapChange = globalStats?.market_cap_change_percentage_24h_usd ?? 0;

  // Top gainers & losers
  const sorted = coins
    ? [...coins].sort(
        (a, b) => (b.price_change_percentage_24h ?? 0) - (a.price_change_percentage_24h ?? 0)
      )
    : [];
  const gainers = sorted.filter((c) => (c.price_change_percentage_24h ?? 0) > 0).slice(0, 5);
  const losers = sorted
    .filter((c) => (c.price_change_percentage_24h ?? 0) < 0)
    .slice(-5)
    .reverse();

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white sm:text-3xl">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Real-time crypto market intelligence
        </p>
      </div>

      {/* KPI Grid */}
      <KPIGrid>
        <KPICard
          title="Total Market Cap"
          value={formatLargeNumber(marketCap)}
          change={marketCapChange}
          icon={DollarSign}
          iconColor="#3B82F6"
          loading={isLoading}
        />
        <KPICard
          title="24h Volume"
          value={formatLargeNumber(totalVolume)}
          change={totalVolume > 0 ? 0 : 0}
          changeLabel="vs yesterday"
          icon={Activity}
          iconColor="#10B981"
          loading={isLoading}
        />
        <KPICard
          title="BTC Dominance"
          value={`${btcDominance.toFixed(1)}%`}
          change={0}
          icon={BarChart3}
          iconColor="#F59E0B"
          loading={isLoading}
        />
        <KPICard
          title="Fear & Greed"
          value={fearGreed?.value?.toString() ?? "50"}
          change={fearGreed ? (fearGreed.value > 50 ? 10 : -10) : 0}
          changeLabel={fearGreed?.classification ?? "Neutral"}
          icon={Gauge}
          iconColor="#8B5CF6"
          loading={isLoading}
        />
      </KPIGrid>

      {/* Top Gainers & Losers */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Gainers */}
        <motion.div variants={item} initial="hidden" animate="show">
          <div className="flex items-center gap-2 mb-4">
            <ArrowUp className="w-5 h-5 text-emerald-500" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Top Gainers (24h)
            </h2>
          </div>
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800">
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Asset</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">24h</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {isLoading
                    ? Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i}>
                          <td className="px-4 py-3"><div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" /></td>
                          <td className="px-4 py-3"><div className="h-4 w-16 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                          <td className="px-4 py-3"><div className="h-4 w-14 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        </tr>
                      ))
                    : gainers.map((coin) => (
                        <tr key={coin.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="px-4 py-3 whitespace-nowrap">
                            <Link href={`/coins/${coin.id}`} className="flex items-center gap-3">
                              <img src={coin.image} alt={coin.name} className="w-7 h-7 rounded-full" />
                              <div>
                                <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                                <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                              </div>
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-right text-sm font-medium text-slate-900 dark:text-white">
                            {formatCurrency(coin.current_price)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Badge variant="bullish" size="sm" className="font-mono">
                              +{coin.price_change_percentage_24h?.toFixed(2)}%
                            </Badge>
                          </td>
                        </tr>
                      ))}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.div>

        {/* Losers */}
        <motion.div variants={item} initial="hidden" animate="show">
          <div className="flex items-center gap-2 mb-4">
            <ArrowDown className="w-5 h-5 text-red-500" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Top Losers (24h)
            </h2>
          </div>
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800">
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Asset</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">24h</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {isLoading
                    ? Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i}>
                          <td className="px-4 py-3"><div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" /></td>
                          <td className="px-4 py-3"><div className="h-4 w-16 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                          <td className="px-4 py-3"><div className="h-4 w-14 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        </tr>
                      ))
                    : losers.map((coin) => (
                        <tr key={coin.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="px-4 py-3 whitespace-nowrap">
                            <Link href={`/coins/${coin.id}`} className="flex items-center gap-3">
                              <img src={coin.image} alt={coin.name} className="w-7 h-7 rounded-full" />
                              <div>
                                <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                                <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                              </div>
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-right text-sm font-medium text-slate-900 dark:text-white">
                            {formatCurrency(coin.current_price)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Badge variant="bearish" size="sm" className="font-mono">
                              {coin.price_change_percentage_24h?.toFixed(2)}%
                            </Badge>
                          </td>
                        </tr>
                      ))}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* All Coins */}
      <motion.div variants={item} initial="hidden" animate="show">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Market Overview
          </h2>
          <Link href="/watchlist">
            <Badge variant="outline" className="text-xs cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800">
              View Watchlist →
            </Badge>
          </Link>
        </div>
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800">
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">#</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Name</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">24h %</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">7d %</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase hidden sm:table-cell">Market Cap</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase hidden md:table-cell">Volume 24h</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {isLoading
                  ? Array.from({ length: 20 }).map((_, i) => (
                      <tr key={i}>
                        <td className="px-4 py-3"><div className="h-4 w-6 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" /></td>
                        <td className="px-4 py-3"><div className="h-4 w-28 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" /></td>
                        <td className="px-4 py-3"><div className="h-4 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        <td className="px-4 py-3"><div className="h-4 w-16 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        <td className="px-4 py-3"><div className="h-4 w-16 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        <td className="px-4 py-3 hidden sm:table-cell"><div className="h-4 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                        <td className="px-4 py-3 hidden md:table-cell"><div className="h-4 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse ml-auto" /></td>
                      </tr>
                    ))
                  : coins?.map((coin, idx) => (
                      <tr
                        key={coin.id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
                      >
                        <td className="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">
                          {coin.market_cap_rank ?? idx + 1}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <Link href={`/coins/${coin.id}`} className="flex items-center gap-3">
                            <img src={coin.image} alt={coin.name} className="w-8 h-8 rounded-full" />
                            <div>
                              <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                              <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                            </div>
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-right text-sm font-medium text-slate-900 dark:text-white tabular-nums">
                          {formatCurrency(coin.current_price)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span
                            className={`text-sm font-mono font-medium tabular-nums ${
                              (coin.price_change_percentage_24h ?? 0) >= 0
                                ? "text-emerald-600 dark:text-emerald-400"
                                : "text-red-600 dark:text-red-400"
                            }`}
                          >
                            {(coin.price_change_percentage_24h ?? 0) >= 0 ? "+" : ""}
                            {coin.price_change_percentage_24h?.toFixed(2) ?? "0.00"}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-sm font-mono text-slate-500 dark:text-slate-400 tabular-nums hidden sm:table-cell">
                          {(coin.price_change_percentage_7d_in_currency ?? 0) >= 0 ? "+" : ""}
                          {coin.price_change_percentage_7d_in_currency?.toFixed(2) ?? "0.00"}%
                        </td>
                        <td className="px-4 py-3 text-right text-sm text-slate-700 dark:text-slate-300 tabular-nums hidden sm:table-cell">
                          {formatLargeNumber(coin.market_cap)}
                        </td>
                        <td className="px-4 py-3 text-right text-sm text-slate-500 dark:text-slate-400 tabular-nums hidden md:table-cell">
                          {formatLargeNumber(coin.total_volume)}
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div className="grid gap-4 sm:grid-cols-2" variants={item} initial="hidden" animate="show">
        <Link href="/coins/bitcoin">
          <Card className="p-6 text-center hover:shadow-lg transition-shadow cursor-pointer">
            <Sparkles className="h-8 w-8 text-blue-500 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Run AI Analysis
            </h3>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Analyze any cryptocurrency with our multi-agent AI system
            </p>
          </Card>
        </Link>
        <Link href="/portfolio">
          <Card className="p-6 text-center hover:shadow-lg transition-shadow cursor-pointer">
            <BarChart3 className="h-8 w-8 text-purple-500 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              View Portfolio
            </h3>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Track your holdings and get AI insights
            </p>
          </Card>
        </Link>
      </motion.div>
    </div>
  );
}
