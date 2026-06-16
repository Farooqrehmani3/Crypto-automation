/**
 * Direct CoinGecko API client (browser-side fallback)
 * Used when the FastAPI backend is unavailable.
 * Respects CoinGecko rate limits.
 */

const COINGECKO_BASE = "https://api.coingecko.com/api/v3";
const DEMO_API_KEY = "CG-fUUVXcpZGgijdkEfJuyU9cU4";

interface CoinGeckoMarketData {
  id: string;
  symbol: string;
  name: string;
  image: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  total_volume: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d_in_currency?: number;
  sparkline_in_7d?: { price: number[] };
}

let lastFetchTime = 0;
const MIN_FETCH_INTERVAL = 15000; // 15 seconds between fetches

async function rateLimitedFetch(url: string): Promise<Response> {
  const now = Date.now();
  const timeSinceLastFetch = now - lastFetchTime;
  if (timeSinceLastFetch < MIN_FETCH_INTERVAL) {
    await new Promise((r) => setTimeout(r, MIN_FETCH_INTERVAL - timeSinceLastFetch));
  }
  lastFetchTime = Date.now();
  return fetch(url);
}

export async function fetchTopCoins(limit = 20): Promise<CoinGeckoMarketData[]> {
  const url = `${COINGECKO_BASE}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=${limit}&page=1&sparkline=true&price_change_percentage=24h,7d&x_cg_demo_api_key=${DEMO_API_KEY}`;

  const res = await rateLimitedFetch(url);
  if (!res.ok) throw new Error(`CoinGecko error: ${res.status}`);
  return res.json();
}

export async function fetchGlobalData() {
  const url = `${COINGECKO_BASE}/global?x_cg_demo_api_key=${DEMO_API_KEY}`;
  const res = await rateLimitedFetch(url);
  if (!res.ok) throw new Error(`CoinGecko error: ${res.status}`);
  return res.json();
}

export async function fetchFearGreedIndex() {
  const res = await fetch("https://api.alternative.me/fng/?limit=1");
  if (!res.ok) return null;
  const data = await res.json();
  if (data?.data?.[0]) {
    return {
      value: parseInt(data.data[0].value),
      classification: data.data[0].value_classification,
    };
  }
  return null;
}

export async function fetchCoinOHLC(coinId: string, days = 30) {
  const url = `${COINGECKO_BASE}/coins/${coinId}/ohlc?vs_currency=usd&days=${days}&x_cg_demo_api_key=${DEMO_API_KEY}`;
  const res = await rateLimitedFetch(url);
  if (!res.ok) throw new Error(`CoinGecko error: ${res.status}`);
  const raw: number[][] = await res.json();

  // Deduplicate and use Unix seconds (lightweight-charts handles this natively)
  const seen = new Set<number>();
  const result: { timestamp: number; open: number; high: number; low: number; close: number; volume: number }[] = [];

  for (const [t, o, h, l, c] of raw) {
    const sec = Math.floor(t / 1000);
    if (seen.has(sec)) continue; // skip duplicates
    seen.add(sec);
    result.push({ timestamp: sec, open: o, high: h, low: l, close: c, volume: 0 });
  }

  return result;
}

export async function searchCoins(query: string) {
  const url = `${COINGECKO_BASE}/search?query=${encodeURIComponent(query)}&x_cg_demo_api_key=${DEMO_API_KEY}`;
  const res = await rateLimitedFetch(url);
  if (!res.ok) throw new Error(`CoinGecko error: ${res.status}`);
  return res.json();
}
