"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import type { ApiResponse, Portfolio, PortfolioAsset, PortfolioTransaction } from "@/lib/types";

export function usePortfolio() {
  return useQuery({
    queryKey: ["portfolio"],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<Portfolio>>("/portfolio");
      return response.data;
    },
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

export function usePortfolioPerformance(period: string = "1m") {
  return useQuery({
    queryKey: ["portfolioPerformance", period],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<any>>(
        `/portfolio/performance?period=${period}`
      );
      return response.data;
    },
    staleTime: 60_000,
  });
}

export function usePortfolioAllocation() {
  return useQuery({
    queryKey: ["portfolioAllocation"],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<any>>("/portfolio/allocation");
      return response.data;
    },
    staleTime: 60_000,
  });
}

export function useAddHolding() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { coin_id: string; quantity: number; average_buy_price: number }) => {
      return apiClient.post("/portfolio/assets", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
      queryClient.invalidateQueries({ queryKey: ["portfolioAllocation"] });
      toast.success("Holding added");
    },
    onError: (error: any) => toast.error(error?.message || "Failed to add holding"),
  });
}

export function useRecordTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      portfolio_asset_id: string;
      type: "buy" | "sell";
      quantity: number;
      price_per_unit: number;
      fee?: number;
      transaction_date: string;
      notes?: string;
    }) => {
      return apiClient.post("/portfolio/transactions", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
      queryClient.invalidateQueries({ queryKey: ["portfolioPerformance"] });
      toast.success("Transaction recorded");
    },
    onError: (error: any) => toast.error(error?.message || "Failed to record transaction"),
  });
}
