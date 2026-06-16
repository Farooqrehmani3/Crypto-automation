"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  change: number;
  changeLabel?: string;
  icon: LucideIcon;
  iconColor?: string;
  sparklineData?: number[];
  sparklineColor?: string;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

function MiniSparkline({
  data,
  color = "#3B82F6",
  positive,
}: {
  data: number[];
  color: string;
  positive: boolean;
}) {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const width = 80;
  const height = 28;
  const padding = 2;

  const points = data
    .map((val, i) => {
      const x = padding + (i / (data.length - 1)) * (width - padding * 2);
      const y =
        height - padding - ((val - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  const areaPoints = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="flex-shrink-0"
    >
      <defs>
        <linearGradient id={`spark-gradient-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.2" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={areaPoints}
        fill={`url(#spark-gradient-${color.replace("#", "")})`}
      />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function KPICard({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  iconColor = "#3B82F6",
  sparklineData,
  sparklineColor,
  loading = false,
  className,
  onClick,
}: KPICardProps) {
  const isPositive = change >= 0;

  if (loading) {
    return (
      <Card className={cn("p-5 space-y-3", className)}>
        <div className="flex items-center justify-between">
          <Skeleton variant="text" width={80} height={14} />
          <Skeleton variant="circular" width={36} height={36} />
        </div>
        <Skeleton variant="text" width={120} height={28} />
        <Skeleton variant="text" width={100} height={18} />
        <Skeleton variant="chart" className="h-8 w-20" />
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={cn(onClick && "cursor-pointer", className)}
    >
      <Card hover="glow" className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
            {title}
          </span>
          <div
            className="flex items-center justify-center w-9 h-9 rounded-xl"
            style={{
              backgroundColor: `${iconColor}15`,
              color: iconColor,
            }}
          >
            <Icon className="w-4 h-4" />
          </div>
        </div>

        {/* Value */}
        <div className="mb-1">
          <span className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            {value}
          </span>
        </div>

        {/* Change + Sparkline */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            {isPositive ? (
              <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5 text-red-500" />
            )}
            <Badge
              variant={isPositive ? "bullish" : "bearish"}
              size="sm"
              className="font-mono"
            >
              {isPositive ? "+" : ""}
              {change.toFixed(2)}%
            </Badge>
            {changeLabel && (
              <span className="text-xs text-slate-400 dark:text-slate-500 ml-1">
                {changeLabel}
              </span>
            )}
          </div>

          {sparklineData && sparklineData.length > 1 && (
            <MiniSparkline
              data={sparklineData}
              color={sparklineColor || (isPositive ? "#10B981" : "#EF4444")}
              positive={isPositive}
            />
          )}
        </div>
      </Card>
    </motion.div>
  );
}

export function KPIGrid({
  children,
  cols = 4,
  className,
}: {
  children: React.ReactNode;
  cols?: 2 | 3 | 4;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "grid gap-4",
        {
          "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4": cols === 4,
          "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3": cols === 3,
          "grid-cols-1 sm:grid-cols-2": cols === 2,
        },
        className
      )}
    >
      {children}
    </div>
  );
}
