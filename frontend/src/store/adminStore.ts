"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AdminUser {
  username: string;
  role: string;
  exp: number;
}

interface AdminState {
  // State
  admin: AdminUser | null;
  token: string | null;
  isLoading: boolean;
  isInitialized: boolean;

  // Actions
  setAdmin: (admin: AdminUser | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  setInitialized: (isInitialized: boolean) => void;
  reset: () => void;
}

export const useAdminStore = create<AdminState>()(
  persist(
    (set) => ({
      // Initial state
      admin: null,
      token: null,
      isLoading: true,
      isInitialized: false,

      // Actions
      setAdmin: (admin) => set({ admin }),
      setToken: (token) => set({ token }),
      setLoading: (isLoading) => set({ isLoading }),
      setInitialized: (isInitialized) => set({ isInitialized }),
      reset: () =>
        set({
          admin: null,
          token: null,
          isLoading: false,
          isInitialized: true,
        }),
    }),
    {
      name: "admin-storage",
      partialize: (state) => ({
        token: state.token,
        admin: state.admin,
      }),
    }
  )
);
