export interface Coin {
  id: string;
  symbol: string;
  name: string;
  image: string;
  currentPrice: number;
  marketCap: number;
  marketCapRank: number;
  fullyDilutedValuation: number | null;
  totalVolume: number;
  high24h: number;
  low24h: number;
  priceChange24h: number;
  priceChangePercentage24h: number;
  priceChangePercentage7d: number;
  priceChangePercentage30d: number;
  marketCapChange24h: number;
  marketCapChangePercentage24h: number;
  circulatingSupply: number;
  totalSupply: number | null;
  maxSupply: number | null;
  ath: number;
  athChangePercentage: number;
  athDate: string;
  atl: number;
  atlChangePercentage: number;
  atlDate: string;
  lastUpdated: string;
  sparkline7d?: Sparkline;
}

export interface CoinPrice {
  coinId: string;
  price: number;
  timestamp: string | number;
  currency: string;
}

export interface CoinStats {
  coinId: string;
  marketCap: number;
  volume24h: number;
  dominance: number;
  rank: number;
  allTimeHigh: number;
  allTimeHighDate: string;
  allTimeHighPercentDown: number;
  circulatingSupply: number;
  totalSupply: number | null;
  maxSupply: number | null;
  fullyDilutedValuation: number | null;
  priceChange24hPercent: number;
  priceChange7dPercent: number;
  priceChange30dPercent: number;
  volatility24h: number;
  sentimentScore: number;
  communityScore: number;
  liquidityScore: number;
}

export interface OHLCVData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Sparkline {
  price: number[];
}

export interface CoinSearchResult {
  id: string;
  symbol: string;
  name: string;
  thumb: string;
  marketCapRank: number;
}

export interface TrendingCoin {
  item: {
    id: string;
    coin_id: number;
    name: string;
    symbol: string;
    market_cap_rank: number;
    thumb: string;
    small: string;
    large: string;
    slug: string;
    price_btc: number;
    score: number;
  };
}
