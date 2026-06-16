"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import type { ApiResponse } from "@/lib/types";

interface Watchlist {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
  items?: WatchlistItem[];
}

interface WatchlistItem {
  id: string;
  coin_id: string;
  is_favorite: boolean;
  coin?: any;
}

export function useWatchlists() {
  return useQuery({
    queryKey: ["watchlists"],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<Watchlist[]>>("/watchlists");
      return response.data;
    },
    staleTime: 30_000,
  });
}

export function useWatchlistItems(watchlistId: string) {
  return useQuery({
    queryKey: ["watchlistItems", watchlistId],
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<WatchlistItem[]>>(
        `/watchlists/${watchlistId}/items`
      );
      return response.data;
    },
    enabled: !!watchlistId,
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useAddToWatchlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      watchlistId,
      coinId,
    }: {
      watchlistId: string;
      coinId: string;
    }) => {
      return apiClient.post(`/watchlists/${watchlistId}/items`, { coin_id: coinId });
    },
    onSuccess: (_, { watchlistId }) => {
      queryClient.invalidateQueries({ queryKey: ["watchlistItems", watchlistId] });
      toast.success("Coin added to watchlist");
    },
    onError: (error: any) => {
      toast.error(error?.message || "Failed to add coin");
    },
  });
}

export function useRemoveFromWatchlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      watchlistId,
      coinId,
    }: {
      watchlistId: string;
      coinId: string;
    }) => {
      return apiClient.delete(`/watchlists/${watchlistId}/items/${coinId}`);
    },
    onSuccess: (_, { watchlistId }) => {
      queryClient.invalidateQueries({ queryKey: ["watchlistItems", watchlistId] });
      toast.success("Coin removed from watchlist");
    },
    onError: (error: any) => {
      toast.error(error?.message || "Failed to remove coin");
    },
  });
}

export function useToggleFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      watchlistId,
      coinId,
      isFavorite,
    }: {
      watchlistId: string;
      coinId: string;
      isFavorite: boolean;
    }) => {
      return apiClient.patch(`/watchlists/${watchlistId}/items/${coinId}`, {
        is_favorite: isFavorite,
      });
    },
    onMutate: async ({ watchlistId, coinId, isFavorite }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ["watchlistItems", watchlistId] });
      const previous = queryClient.getQueryData(["watchlistItems", watchlistId]);
      queryClient.setQueryData(["watchlistItems", watchlistId], (old: any) => {
        if (!old) return old;
        return old.map((item: WatchlistItem) =>
          item.coin_id === coinId ? { ...item, is_favorite: isFavorite } : item
        );
      });
      return { previous };
    },
    onError: (err: any, { watchlistId }, context) => {
      queryClient.setQueryData(["watchlistItems", watchlistId], context?.previous);
      toast.error("Failed to update favorite");
    },
    onSettled: (_, __, { watchlistId }) => {
      queryClient.invalidateQueries({ queryKey: ["watchlistItems", watchlistId] });
    },
  });
}
