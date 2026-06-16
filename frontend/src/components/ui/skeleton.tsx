"use client";

import { cn } from "@/lib/utils/cn";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular" | "card" | "chart" | "table-row";
  width?: string | number;
  height?: string | number;
  animation?: "pulse" | "wave" | "none";
}

function Skeleton({
  className,
  variant = "text",
  width,
  height,
  animation = "pulse",
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cn(
        "bg-slate-200 dark:bg-slate-800",
        {
          "animate-pulse rounded-md": animation === "pulse",
          "animate-shimmer rounded-md bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] dark:from-slate-800 dark:via-slate-700 dark:to-slate-800":
            animation === "wave",
          "rounded-full": variant === "circular",
          "rounded-md": variant === "text" || variant === "rectangular",
          "rounded-xl": variant === "card",
          "rounded-lg h-64": variant === "chart",
          "rounded h-12": variant === "table-row",
        },
        className
      )}
      style={{ width, height }}
      {...props}
    />
  );
}

function CardSkeleton() {
  return (
    <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width={100} height={16} />
        <Skeleton variant="circular" width={32} height={32} />
      </div>
      <Skeleton variant="text" width={140} height={28} />
      <div className="flex items-center gap-2">
        <Skeleton variant="text" width={60} height={20} />
        <Skeleton variant="text" width={80} height={14} />
      </div>
      <Skeleton variant="chart" className="h-12" />
    </div>
  );
}

function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-3">
      <div className="flex gap-4 px-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={`h-${i}`} variant="text" width={80} height={14} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-4 px-4 py-3">
          {Array.from({ length: cols }).map((_, c) => (
            <Skeleton
              key={`${r}-${c}`}
              variant="text"
              width={c === 0 ? 120 : 80}
              height={14}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800/60 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width={150} height={20} />
        <div className="flex gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="text" width={40} height={28} />
          ))}
        </div>
      </div>
      <Skeleton variant="chart" className="h-80" />
    </div>
  );
}

function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width={200} height={32} />
        <Skeleton variant="text" width={120} height={40} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  );
}

export { Skeleton, CardSkeleton, TableSkeleton, ChartSkeleton, PageSkeleton };
