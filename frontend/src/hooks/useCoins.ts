"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { Coin, CoinPrice, ApiResponse, PaginatedResponse } from "@/lib/types";

// --- Coin List ---
export function useCoins(params?: {
  page?: number;
  perPage?: number;
  sortBy?: string;
  search?: string;
}) {
  return useQuery({
    queryKey: ["coins", params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set("page", String(params.page));
      if (params?.perPage) searchParams.set("per_page", String(params.perPage));
      if (params?.sortBy) searchParams.set("sort_by", params.sortBy);
      if (params?.search) searchParams.set("search", params.search);

      const response = await apiClient.get<PaginatedResponse<Coin>>(
        `/coins?${searchParams.toString()}`
      );
      return response;
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

// --- Coin Detail ---
export function useCoinDetail(coinId: string) {
  return useQuery({
    queryKey: ["coin", coinId],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<Coin>>(`/coins/${coinId}`);
      return response.data;
    },
    enabled: !!coinId,
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

// --- Coin Prices (OHLCV) ---
export function useCoinPrices(
  coinId: string,
  timeframe: string = "1d",
  limit: number = 100
) {
  return useQuery({
    queryKey: ["coinPrices", coinId, timeframe, limit],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<CoinPrice[]>>(
        `/coins/${coinId}/prices?timeframe=${timeframe}&limit=${limit}`
      );
      return response.data;
    },
    enabled: !!coinId,
    staleTime: 15_000,
    refetchInterval: timeframe === "1m" ? 10_000 : 30_000,
  });
}

// --- Market Overview ---
export function useMarketOverview() {
  return useQuery({
    queryKey: ["marketOverview"],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<any>>("/market/overview");
      return response.data;
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

// --- Top Movers ---
export function useTopMovers(direction: "gainers" | "losers" = "gainers", limit = 10) {
  return useQuery({
    queryKey: ["topMovers", direction, limit],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<Coin[]>>(
        `/market/top-movers?direction=${direction}&limit=${limit}`
      );
      return response.data;
    },
    staleTime: 60_000,
    refetchInterval: 120_000,
  });
}

// --- Search ---
export function useCoinSearch(query: string) {
  return useQuery({
    queryKey: ["coinSearch", query],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<Coin[]>>(
        `/market/search?q=${encodeURIComponent(query)}&limit=20`
      );
      return response.data;
    },
    enabled: query.length >= 2,
    staleTime: 60_000,
  });
}
