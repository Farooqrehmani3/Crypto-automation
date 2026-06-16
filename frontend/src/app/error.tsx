"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error("Global error boundary caught:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-white dark:bg-secondary-950">
      <motion.div
        className="flex flex-col items-center text-center max-w-md"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-red-50 dark:bg-red-950/50 ring-1 ring-red-200 dark:ring-red-900">
          <AlertTriangle className="h-10 w-10 text-red-500" />
        </div>

        <h1 className="text-2xl font-bold text-secondary-900 dark:text-white">
          Something went wrong
        </h1>
        <p className="mt-2 text-secondary-500 dark:text-secondary-400">
          {error.message || "An unexpected error occurred. Please try again."}
        </p>

        {error.digest && (
          <p className="mt-1 text-xs text-secondary-400">
            Error ID: {error.digest}
          </p>
        )}

        <div className="mt-8 flex flex-col sm:flex-row gap-3">
          <Button onClick={reset} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <Home className="h-4 w-4" />
              Go Home
            </Button>
          </Link>
        </div>

        <p className="mt-8 text-xs text-secondary-400">
          If this problem persists, please contact{" "}
          <a
            href="mailto:support@cryptointelligence.ai"
            className="underline hover:text-secondary-500"
          >
            support@cryptointelligence.ai
          </a>
        </p>
      </motion.div>
    </div>
  );
}
