"use client";

import { create } from "zustand";

export type Timeframe = "1H" | "24H" | "7D" | "30D" | "90D" | "1Y" | "ALL";
export type ChartIndicator =
  | "none"
  | "rsi"
  | "macd"
  | "bollinger"
  | "ema"
  | "sma"
  | "volume";

interface MarketState {
  // Selected coin
  selectedCoinId: string | null;
  setSelectedCoinId: (coinId: string | null) => void;

  // Timeframe
  selectedTimeframe: Timeframe;
  setSelectedTimeframe: (timeframe: Timeframe) => void;

  // Chart indicators
  enabledIndicators: ChartIndicator[];
  toggleIndicator: (indicator: ChartIndicator) => void;
  setIndicators: (indicators: ChartIndicator[]) => void;

  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchResults: string[];
  setSearchResults: (results: string[]) => void;

  // Market data
  marketCap: string;
  volume24h: string;
  btcDominance: number;
  setMarketOverview: (data: { marketCap: string; volume24h: string; btcDominance: number }) => void;
}

export const useMarketStore = create<MarketState>()((set) => ({
  // Selected coin
  selectedCoinId: null,
  setSelectedCoinId: (coinId) => set({ selectedCoinId: coinId }),

  // Timeframe
  selectedTimeframe: "24H",
  setSelectedTimeframe: (timeframe) => set({ selectedTimeframe: timeframe }),

  // Chart indicators
  enabledIndicators: [],
  toggleIndicator: (indicator) =>
    set((state) => ({
      enabledIndicators: state.enabledIndicators.includes(indicator)
        ? state.enabledIndicators.filter((i) => i !== indicator)
        : [...state.enabledIndicators, indicator],
    })),
  setIndicators: (indicators) => set({ enabledIndicators: indicators }),

  // Search
  searchQuery: "",
  setSearchQuery: (query) => set({ searchQuery: query }),
  searchResults: [],
  setSearchResults: (results) => set({ searchResults: results }),

  // Market data
  marketCap: "$0",
  volume24h: "$0",
  btcDominance: 0,
  setMarketOverview: (data) =>
    set({
      marketCap: data.marketCap,
      volume24h: data.volume24h,
      btcDominance: data.btcDominance,
    }),
}));
