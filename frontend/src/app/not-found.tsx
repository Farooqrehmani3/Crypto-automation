"use client";

import { motion } from "framer-motion";
import { Search, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-white dark:bg-secondary-950">
      <motion.div
        className="flex flex-col items-center text-center max-w-md"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* 404 Visual */}
        <div className="relative mb-8">
          <div className="text-8xl font-bold text-gradient select-none">404</div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Search className="h-12 w-12 text-blue-500/30" />
          </div>
        </div>

        <h1 className="text-2xl font-bold text-secondary-900 dark:text-white">
          Page not found
        </h1>
        <p className="mt-2 text-secondary-500 dark:text-secondary-400">
          Sorry, we couldn&apos;t find the page you&apos;re looking for. It might have been
          moved, deleted, or never existed.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row gap-3">
          <Link href="/dashboard">
            <Button className="gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
              Go to Dashboard
            </Button>
          </Link>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back Home
            </Button>
          </Link>
        </div>

        <div className="mt-12 p-4 rounded-xl bg-secondary-50 dark:bg-secondary-900/50 border border-secondary-200 dark:border-secondary-800">
          <p className="text-xs text-secondary-400 mb-2">Quick Links</p>
          <div className="flex flex-wrap justify-center gap-3 text-sm">
            <Link
              href="/dashboard"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Dashboard
            </Link>
            <Link
              href="/watchlist"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Watchlist
            </Link>
            <Link
              href="/portfolio"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Portfolio
            </Link>
            <Link
              href="/settings"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Settings
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
