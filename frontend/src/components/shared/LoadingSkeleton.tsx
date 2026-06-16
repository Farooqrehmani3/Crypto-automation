"use client";

import { cn } from "@/lib/utils/cn";

type SkeletonVariant = "card" | "table" | "chart" | "text" | "sidebar" | "dashboard" | "list";

interface LoadingSkeletonProps {
  variant?: SkeletonVariant;
  className?: string;
  count?: number;
}

function SkeletonBlock({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return (
    <div className={cn("animate-skeleton rounded-lg bg-secondary-200 dark:bg-secondary-700", className)} style={style} />
  );
}

function CardSkeleton() {
  return (
    <div className="glass-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <SkeletonBlock className="h-3 w-24" />
        <SkeletonBlock className="h-8 w-8 rounded-lg" />
      </div>
      <SkeletonBlock className="h-8 w-32" />
      <SkeletonBlock className="h-3 w-20" />
    </div>
  );
}

function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-4 p-4 border-b border-secondary-200 dark:border-secondary-800">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-3 w-20" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 p-4 border-b border-secondary-100 dark:border-secondary-800/50 last:border-0"
        >
          <SkeletonBlock className="h-8 w-8 rounded-full" />
          <div className="space-y-2 flex-1">
            <SkeletonBlock className="h-3 w-32" />
            <SkeletonBlock className="h-2 w-16" />
          </div>
          <SkeletonBlock className="h-3 w-20" />
          <SkeletonBlock className="h-3 w-16" />
          <SkeletonBlock className="h-3 w-12" />
        </div>
      ))}
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="glass-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <SkeletonBlock className="h-4 w-32" />
        <div className="flex gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonBlock key={i} className="h-6 w-10 rounded-md" />
          ))}
        </div>
      </div>
      <div className="relative h-64">
        {/* Simulated chart lines */}
        <div className="absolute inset-0 flex items-end gap-1">
          {Array.from({ length: 30 }).map((_, i) => {
            // Deterministic pseudo-random using index (avoids hydration mismatch)
            const height = 20 + ((i * 17 + i * i * 3) % 80);
            return (
              <SkeletonBlock
                key={i}
                className="flex-1 rounded-sm"
                style={{ height: `${height}%` }}
              />
            );
          })}
        </div>
      </div>
      <div className="flex justify-between">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-2 w-8" />
        ))}
      </div>
    </div>
  );
}

function TextSkeleton() {
  return (
    <div className="space-y-2">
      <SkeletonBlock className="h-4 w-3/4" />
      <SkeletonBlock className="h-4 w-full" />
      <SkeletonBlock className="h-4 w-5/6" />
      <SkeletonBlock className="h-4 w-2/3" />
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <div className="space-y-6">
      {/* Logo area */}
      <div className="flex items-center gap-2">
        <SkeletonBlock className="h-8 w-8 rounded-lg" />
        <SkeletonBlock className="h-4 w-24" />
      </div>

      {/* Nav items */}
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-9 w-full rounded-lg" />
        ))}
      </div>

      <div className="border-t border-secondary-200 dark:border-secondary-800 pt-4">
        <SkeletonBlock className="h-3 w-16 mb-2" />
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-8 w-full rounded-lg mb-1" />
        ))}
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>

      {/* Chart area */}
      <ChartSkeleton />

      {/* Table */}
      <TableSkeleton rows={5} />
    </div>
  );
}

function ListSkeleton({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 rounded-lg">
          <SkeletonBlock className="h-8 w-8 rounded-full shrink-0" />
          <div className="space-y-1.5 flex-1">
            <SkeletonBlock className="h-3 w-32" />
            <SkeletonBlock className="h-2 w-20" />
          </div>
          <SkeletonBlock className="h-3 w-16" />
        </div>
      ))}
    </div>
  );
}

export function LoadingSkeleton({
  variant = "card",
  className,
  count,
}: LoadingSkeletonProps) {
  if (count && count > 1) {
    const items = Array.from({ length: count });
    return (
      <div className={cn("grid gap-4", className)}>
        {items.map((_, i) => (
          <LoadingSkeleton key={i} variant={variant} />
        ))}
      </div>
    );
  }

  switch (variant) {
    case "card":
      return <CardSkeleton />;
    case "table":
      return <TableSkeleton />;
    case "chart":
      return <ChartSkeleton />;
    case "text":
      return <TextSkeleton />;
    case "sidebar":
      return <SidebarSkeleton />;
    case "dashboard":
      return <DashboardSkeleton />;
    case "list":
      return <ListSkeleton />;
    default:
      return <CardSkeleton />;
  }
}
