"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/store/uiStore";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading, isInitialized } = useAuth();
  const isSidebarCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const router = useRouter();

  useEffect(() => {
    if (isInitialized && !isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isInitialized, isLoading, isAuthenticated, router]);

  // Show loading skeleton while auth is initializing
  if (!isInitialized || isLoading) {
    return (
      <div className="flex min-h-screen bg-white dark:bg-secondary-950">
        <div className="w-64 shrink-0 border-r border-secondary-200 dark:border-secondary-800 p-6 hidden lg:block">
          <LoadingSkeleton variant="sidebar" />
        </div>
        <div className="flex-1 flex flex-col">
          <div className="h-16 border-b border-secondary-200 dark:border-secondary-800 p-4">
            <LoadingSkeleton variant="text" />
          </div>
          <div className="flex-1 p-6">
            <LoadingSkeleton variant="dashboard" />
          </div>
        </div>
      </div>
    );
  }

  // Don't render dashboard if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-secondary-50 dark:bg-secondary-950">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          isSidebarCollapsed ? "lg:ml-20" : "lg:ml-64"
        }`}
      >
        {/* Navbar */}
        <Navbar />

        {/* Page Content */}
        <motion.main
          className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="mx-auto max-w-7xl">{children}</div>
        </motion.main>
      </div>
    </div>
  );
}
