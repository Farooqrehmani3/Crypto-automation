"use client";

import { create } from "zustand";

export type ThemeMode = "light" | "dark" | "system";

interface UIState {
  // Sidebar
  isSidebarOpen: boolean;
  isSidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;

  // Theme
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;

  // Modals
  activeModal: string | null;
  openModal: (modalId: string) => void;
  closeModal: () => void;

  // Search
  isSearchOpen: boolean;
  setSearchOpen: (open: boolean) => void;

  // Notifications
  unreadNotifications: number;
  setUnreadNotifications: (count: number) => void;
  incrementNotifications: () => void;
  resetNotifications: () => void;
}

export const useUIStore = create<UIState>()((set) => ({
  // Sidebar
  isSidebarOpen: true,
  isSidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({
      isSidebarOpen: !state.isSidebarOpen,
      isSidebarCollapsed: !state.isSidebarCollapsed,
    })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  setSidebarCollapsed: (collapsed) => set({ isSidebarCollapsed: collapsed }),

  // Theme
  theme: "system",
  setTheme: (theme) => set({ theme }),

  // Modals
  activeModal: null,
  openModal: (modalId) => set({ activeModal: modalId }),
  closeModal: () => set({ activeModal: null }),

  // Search
  isSearchOpen: false,
  setSearchOpen: (open) => set({ isSearchOpen: open }),

  // Notifications
  unreadNotifications: 0,
  setUnreadNotifications: (count) => set({ unreadNotifications: count }),
  incrementNotifications: () =>
    set((state) => ({ unreadNotifications: state.unreadNotifications + 1 })),
  resetNotifications: () => set({ unreadNotifications: 0 }),
}));
