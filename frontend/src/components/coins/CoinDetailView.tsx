"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  TrendingUp, TrendingDown, Star, Bell, Sparkles,
  BarChart3, Activity, DollarSign, Layers, ExternalLink,
  Loader2, Brain, AlertTriangle, Shield, Newspaper, Globe,
  TrendingUp as ForecastIcon, FileText,
} from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { PriceBadge } from "@/components/shared/PriceBadge";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { MarkdownRenderer } from "@/components/shared/MarkdownRenderer";
import { fetchCoinOHLC } from "@/lib/api/coingecko-direct";
import { formatCurrency, formatLargeNumber, formatPercentage } from "@/lib/utils/formatters";

const COINGECKO_BASE = "https://api.coingecko.com/api/v3";
const DEMO_API_KEY = "CG-fUUVXcpZGgijdkEfJuyU9cU4";

interface CoinDetailViewProps {
  coinId: string;
}

// Fetch coin detail from CoinGecko
async function fetchCoinDetail(coinId: string) {
  const url = `${COINGECKO_BASE}/coins/${coinId}?localization=false&tickers=false&community_data=false&developer_data=false&x_cg_demo_api_key=${DEMO_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`CoinGecko error: ${res.status}`);
  return res.json();
}

export function CoinDetailView({ coinId }: CoinDetailViewProps) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [activeTab, setActiveTab] = useState("chart");
  const [timeframe, setTimeframe] = useState("1d");
  const [indicators, setIndicators] = useState({
    volume: true,
    ema20: true,
    ema50: true,
    bollinger: false,
  });

  // AI Analysis state
  const [aiResult, setAiResult] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiActiveTab, setAiActiveTab] = useState("technical");

  // Fetch coin detail
  const { data: coin, isLoading } = useQuery({
    queryKey: ["coinDetail", coinId],
    queryFn: () => fetchCoinDetail(coinId),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  // Fetch OHLCV data
  const daysMap: Record<string, string> = {
    "1h": "1", "4h": "1", "1d": "30", "1w": "90", "1M": "365",
  };
  const { data: ohlcData } = useQuery({
    queryKey: ["coinOHLC", coinId, timeframe],
    queryFn: () => fetchCoinOHLC(coinId, parseInt(daysMap[timeframe] || "30")),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  const runAIAnalysis = useCallback(async () => {
    if (!coin) return;
    setAiLoading(true);
    setActiveTab("analysis");
    setAiResult(null);

    try {
      const marketData = coin.market_data;
      const currentPrice = marketData?.current_price?.usd ?? 0;
      const priceChange24h = marketData?.price_change_percentage_24h ?? 0;
      const priceChange7d = marketData?.price_change_percentage_7d ?? 0;
      const high24h = marketData?.high_24h?.usd ?? 0;
      const low24h = marketData?.low_24h?.usd ?? 0;
      const marketCap = marketData?.market_cap?.usd ?? 0;
      const volume = marketData?.total_volume?.usd ?? 0;
      const ath = marketData?.ath?.usd ?? 0;
      const atl = marketData?.atl?.usd ?? 0;

      const prompt = `You are a professional cryptocurrency analyst. Analyze ${coin.name} (${coin.symbol.toUpperCase()}) with the following real-time market data:

**Current Price:** $${currentPrice.toLocaleString()}
**24h Change:** ${priceChange24h.toFixed(2)}%
**7d Change:** ${priceChange7d.toFixed(2)}%
**24h High:** $${high24h.toLocaleString()}
**24h Low:** $${low24h.toLocaleString()}
**Market Cap:** $${(marketCap / 1e9).toFixed(2)}B
**24h Volume:** $${(volume / 1e9).toFixed(2)}B
**All-Time High:** $${ath.toLocaleString()}
**All-Time Low:** $${atl.toLocaleString()}
**Market Cap Rank:** ${coin.market_cap_rank}

Please provide a comprehensive analysis in the following format:

## TECHNICAL ANALYSIS
- Overall signal (Bullish/Bearish/Neutral) with confidence percentage
- Key support and resistance levels based on recent price action
- Trend analysis (short-term and medium-term)
- Key observations (3-5 bullet points)

## PRICE FORECAST
- 24-hour forecast: Expected High and Low with confidence %
- 3-day outlook with expected range
- 7-day outlook with expected range

## RISK ASSESSMENT
- Risk level (Low/Moderate/High/Extreme)
- Key risk factors (2-3 points)
- Position sizing recommendation

## KEY CATALYSTS
- What could drive price higher (2-3 catalysts)
- What could drive price lower (2-3 risks)

## SUMMARY
- One-paragraph investment thesis
- Overall rating: Strong Buy / Buy / Hold / Sell / Strong Sell`;

      const response = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          coinName: name,
          coinSymbol: symbol,
          prompt,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `API error: ${response.status}`);
      }

      const data = await response.json();
      setAiResult(data.result);
    } catch (err: any) {
      setAiResult(`**Error running analysis:** ${err.message}

Please ensure:
- The OpenAI API key is valid
- You have sufficient API credits
- The backend or direct API access is configured`);
    } finally {
      setAiLoading(false);
    }
  }, [coin]);

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-6 w-32 bg-slate-200 dark:bg-slate-700 rounded" />
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-slate-200 dark:bg-slate-700" />
          <div>
            <div className="h-8 w-48 bg-slate-200 dark:bg-slate-700 rounded mb-2" />
            <div className="h-12 w-36 bg-slate-200 dark:bg-slate-700 rounded" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-20 bg-slate-200 dark:bg-slate-700 rounded-xl" />
          ))}
        </div>
        <div className="h-96 bg-slate-200 dark:bg-slate-700 rounded-xl" />
      </div>
    );
  }

  if (!coin) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Coin not found</h2>
        <p className="text-slate-500 mt-2">Could not find data for "{coinId}"</p>
        <Link href="/dashboard" className="text-blue-500 hover:underline mt-4 inline-block">Back to Dashboard</Link>
      </div>
    );
  }

  const m = coin.market_data;
  const name = coin.name;
  const symbol = coin.symbol?.toUpperCase();
  const image = coin.image?.large;
  const rank = coin.market_cap_rank;
  const price = m?.current_price?.usd ?? 0;
  const change24h = m?.price_change_percentage_24h ?? 0;
  const change7d = m?.price_change_percentage_7d ?? 0;
  const change30d = m?.price_change_percentage_30d ?? 0;
  const high24h = m?.high_24h?.usd ?? 0;
  const low24h = m?.low_24h?.usd ?? 0;
  const marketCap = m?.market_cap?.usd ?? 0;
  const volume = m?.total_volume?.usd ?? 0;
  const circSupply = m?.circulating_supply ?? 0;
  const totalSupply = m?.total_supply;
  const maxSupply = m?.max_supply;
  const ath = m?.ath?.usd ?? 0;
  const athDate = m?.ath_date?.usd;
  const atl = m?.atl?.usd ?? 0;
  const sparkline7d = coin.sparkline_7d || [];

  const description = coin.description?.en?.split(". ").slice(0, 3).join(". ") + ".";

  const aiTabItems = [
    { id: "technical", label: "Technical", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "forecast", label: "Forecast", icon: <ForecastIcon className="w-4 h-4" /> },
    { id: "risk", label: "Risk", icon: <Shield className="w-4 h-4" /> },
    { id: "catalysts", label: "Catalysts", icon: <Newspaper className="w-4 h-4" /> },
  ];

  const mainTabItems = [
    { id: "chart", label: "Price Chart" },
    { id: "analysis", label: "AI Analysis" },
    { id: "about", label: "About" },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Link href="/dashboard" className="hover:text-slate-700 dark:hover:text-slate-300">Dashboard</Link>
        <span>/</span>
        <span className="text-slate-900 dark:text-white font-medium">{name}</span>
      </div>

      {/* Coin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {image ? (
            <img src={image} alt={name} className="h-12 w-12 rounded-full" />
          ) : (
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-lg font-bold text-white">
              {symbol?.charAt(0)}
            </div>
          )}
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{name}</h1>
              <Badge variant="neutral" size="sm">{symbol}</Badge>
              {rank && <Badge variant="neutral" size="sm">Rank #{rank}</Badge>}
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-3xl font-bold text-slate-900 dark:text-white tabular-nums">
                {formatCurrency(price)}
              </span>
              <PriceBadge value={change24h} showIcon size="lg" />
              <span className="text-sm text-slate-500">(24h)</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2" onClick={() => setIsFavorite(!isFavorite)}>
            <Star className={`h-4 w-4 ${isFavorite ? "fill-yellow-400 text-yellow-400" : ""}`} />
            {isFavorite ? "Saved" : "Watch"}
          </Button>
          <Button size="sm" className="gap-2" variant="premium" onClick={runAIAnalysis} disabled={aiLoading}>
            {aiLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            AI Analysis
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
        {[
          { label: "Market Cap", value: formatLargeNumber(marketCap), icon: DollarSign },
          { label: "24h Volume", value: formatLargeNumber(volume), icon: Activity },
          { label: "24h High / Low", value: `${formatCurrency(high24h)} / ${formatCurrency(low24h)}`, icon: TrendingUp },
          { label: "7d Change", value: formatPercentage(change7d), icon: TrendingUp, color: change7d >= 0 ? "text-emerald-500" : "text-red-500" },
          { label: "30d Change", value: formatPercentage(change30d), icon: TrendingUp, color: change30d >= 0 ? "text-emerald-500" : "text-red-500" },
          { label: "All-Time High", value: formatCurrency(ath), icon: BarChart3 },
        ].map((stat, i) => (
          <Card key={i} className="p-4">
            <div className="flex items-center gap-2 mb-1">
              <stat.icon className="h-3.5 w-3.5 text-slate-400" />
              <p className="text-xs text-slate-500">{stat.label}</p>
            </div>
            <p className={`text-sm font-semibold text-slate-900 dark:text-white tabular-nums ${stat.color || ""}`}>
              {stat.value}
            </p>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <div>
        <Tabs tabs={mainTabItems} activeTab={activeTab} onChange={setActiveTab} variant="underline" className="mb-6" />

        <div className="mt-4">
          {/* Price Chart Tab */}
          {activeTab === "chart" && (
            <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="p-4">
                {/* Timeframe Selector */}
                <div className="flex items-center gap-1 mb-4 flex-wrap">
                  {["1h", "4h", "1d", "1w", "1M"].map((tf) => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                        timeframe === tf
                          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                          : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                  <span className="mx-2 text-slate-300">|</span>
                  {Object.entries(indicators).map(([key, enabled]) => (
                    <label key={key} className="flex items-center gap-1.5 text-xs text-slate-500 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={() => setIndicators((prev) => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      />
                      {key === "ema20" ? "EMA 20" : key === "ema50" ? "EMA 50" : key === "bollinger" ? "Bollinger" : "Volume"}
                    </label>
                  ))}
                </div>

                {/* Chart */}
                {ohlcData && ohlcData.length > 0 ? (
                  <CandlestickChart data={ohlcData} indicators={indicators} height={500} />
                ) : (
                  <div className="flex items-center justify-center h-96 text-slate-400">
                    <Loader2 className="h-8 w-8 animate-spin" />
                  </div>
                )}
              </Card>
            </motion.div>
          )}

          {/* AI Analysis Tab */}
          {activeTab === "analysis" && (
            <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}>
              {aiLoading ? (
                <Card className="p-12 text-center">
                  <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Running AI Analysis...</h3>
                  <p className="text-sm text-slate-500">Analyzing {name} market data with GPT-4o</p>
                  <div className="flex items-center justify-center gap-2 mt-3 text-xs text-slate-400">
                    <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                    Technical Analysis
                    <div className="h-2 w-2 rounded-full bg-slate-300 animate-pulse ml-2" />
                    Price Forecast
                    <div className="h-2 w-2 rounded-full bg-slate-300 animate-pulse ml-2" />
                    Risk Assessment
                  </div>
                </Card>
              ) : aiResult ? (
                <Card className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-purple-500" />
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">AI Analysis Report</h3>
                    </div>
                    <Button variant="outline" size="sm" onClick={runAIAnalysis}>
                      <Sparkles className="h-4 w-4 mr-1" /> Re-run
                    </Button>
                  </div>
                  <MarkdownRenderer text={aiResult} />
                </Card>
              ) : (
                <Card className="p-12 text-center" variant="gradient">
                  <Sparkles className="h-12 w-12 text-blue-500 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Multi-Agent AI Analysis
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mb-4 max-w-md mx-auto">
                    Get institutional-grade analysis for {name} including technical signals, price forecasts, risk assessment, and key catalysts — powered by GPT-4o.
                  </p>
                  <Button className="gap-2" variant="premium" onClick={runAIAnalysis}>
                    <Sparkles className="h-4 w-4" />
                    Start Analysis
                  </Button>
                  <p className="text-xs text-slate-400 mt-3">Uses OpenAI GPT-4o • Takes ~10-15 seconds</p>
                </Card>
              )}
            </motion.div>
          )}

          {/* About Tab */}
          {activeTab === "about" && (
            <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">About {name}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                  {description || `${name} (${symbol}) is a cryptocurrency traded on global markets.`}
                </p>
                <div className="grid gap-4 sm:grid-cols-2 text-sm">
                  <div className="space-y-2">
                    <div className="flex justify-between"><span className="text-slate-500">Circulating Supply</span><span className="font-medium text-slate-900 dark:text-white">{circSupply?.toLocaleString()}</span></div>
                    {totalSupply && <div className="flex justify-between"><span className="text-slate-500">Total Supply</span><span className="font-medium text-slate-900 dark:text-white">{totalSupply.toLocaleString()}</span></div>}
                    {maxSupply && <div className="flex justify-between"><span className="text-slate-500">Max Supply</span><span className="font-medium text-slate-900 dark:text-white">{maxSupply.toLocaleString()}</span></div>}
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between"><span className="text-slate-500">All-Time High</span><span className="font-medium text-slate-900 dark:text-white">{formatCurrency(ath)}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">ATH Date</span><span className="font-medium text-slate-900 dark:text-white">{athDate ? new Date(athDate).toLocaleDateString() : "N/A"}</span></div>
                    <div className="flex justify-between"><span className="text-slate-500">All-Time Low</span><span className="font-medium text-slate-900 dark:text-white">{formatCurrency(atl)}</span></div>
                  </div>
                </div>
                <div className="mt-4 flex gap-4">
                  <a href={`https://www.coingecko.com/en/coins/${coinId}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline">
                    View on CoinGecko <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
