"use client";

import { Toaster } from "sonner";
import { useMediaQuery } from "@/hooks/useMediaQuery";

export function ToastProvider() {
  const isDark = useMediaQuery("(prefers-color-scheme: dark)");

  return (
    <Toaster
      position="top-right"
      richColors
      closeButton
      expand={false}
      visibleToasts={5}
      duration={4000}
      theme={isDark ? "dark" : "light"}
      toastOptions={{
        classNames: {
          toast: "group glass-card rounded-xl border-none shadow-lg",
          title: "text-sm font-semibold",
          description: "text-xs text-secondary-500 dark:text-secondary-400",
          success: "!text-green-500",
          error: "!text-red-500",
          warning: "!text-yellow-500",
          info: "!text-blue-500",
        },
      }}
    />
  );
}
