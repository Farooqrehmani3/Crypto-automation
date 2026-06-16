import type { Timeframe } from "@/store/marketStore";

export const APP_NAME = "TecFlux";
export const APP_DESCRIPTION = "AI-powered cryptocurrency analytics and predictive forecasting platform";
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const TIMEFRAMES: { value: Timeframe; label: string; days: number }[] = [
  { value: "1H", label: "1H", days: 0.04 },
  { value: "24H", label: "24H", days: 1 },
  { value: "7D", label: "7D", days: 7 },
  { value: "30D", label: "30D", days: 30 },
  { value: "90D", label: "90D", days: 90 },
  { value: "1Y", label: "1Y", days: 365 },
  { value: "ALL", label: "ALL", days: 1825 },
];

export const DEFAULT_COINS = [
  { id: "bitcoin", symbol: "btc", name: "Bitcoin" },
  { id: "ethereum", symbol: "eth", name: "Ethereum" },
  { id: "binancecoin", symbol: "bnb", name: "BNB" },
  { id: "ripple", symbol: "xrp", name: "XRP" },
  { id: "solana", symbol: "sol", name: "Solana" },
  { id: "cardano", symbol: "ada", name: "Cardano" },
  { id: "avalanche-2", symbol: "avax", name: "Avalanche" },
  { id: "polkadot", symbol: "dot", name: "Polkadot" },
  { id: "dogecoin", symbol: "doge", name: "Dogecoin" },
  { id: "chainlink", symbol: "link", name: "Chainlink" },
];

export const CHART_COLORS = {
  up: "#10b981",
  down: "#ef4444",
  neutral: "#64748b",
  volume: "#3b82f640",
  bullish: {
    primary: "#10b981",
    gradient: ["#10b981", "#34d399"],
  },
  bearish: {
    primary: "#ef4444",
    gradient: ["#ef4444", "#f87171"],
  },
  indicators: {
    rsi: "#8b5cf6",
    macd: "#06b6d4",
    ema: "#f97316",
    sma: "#eab308",
    bollinger: "#3b82f6",
    volume: "#64748b",
  },
  portfolio: [
    "#3b82f6",
    "#06b6d4",
    "#8b5cf6",
    "#f97316",
    "#eab308",
    "#10b981",
    "#ef4444",
    "#ec4899",
    "#6366f1",
    "#14b8a6",
  ],
  dark: {
    background: "#0f172a",
    surface: "#1e293b",
    grid: "#334155",
    text: "#94a3b8",
  },
  light: {
    background: "#ffffff",
    surface: "#f8fafc",
    grid: "#e2e8f0",
    text: "#64748b",
  },
} as const;

export const ANALYTICS_CARD_ITEMS = [
  { key: "marketCap", label: "Market Cap" },
  { key: "volume24h", label: "24h Volume" },
  { key: "circulatingSupply", label: "Circulating Supply" },
  { key: "allTimeHigh", label: "All-Time High" },
] as const;

export const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: "LayoutDashboard",
  },
  {
    label: "Watchlist",
    href: "/watchlist",
    icon: "Star",
  },
  {
    label: "Portfolio",
    href: "/portfolio",
    icon: "Briefcase",
  },
  {
    label: "Settings",
    href: "/settings",
    icon: "Settings",
  },
] as const;

export const MAX_WATCHLIST_COINS = 50;
export const MAX_PORTFOLIO_ASSETS = 100;
export const SEARCH_DEBOUNCE_MS = 300;
export const POLLING_INTERVAL_MS = 3000;
export const CACHE_STALE_TIME_MS = 30_000; // 30 seconds
export const CACHE_GC_TIME_MS = 300_000; // 5 minutes
