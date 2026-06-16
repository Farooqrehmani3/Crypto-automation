"use client";

import { cn } from "@/lib/utils/cn";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { formatPercentage, formatCurrency } from "@/lib/utils/formatters";

interface PriceBadgeProps {
  value: number;
  type?: "percentage" | "currency";
  size?: "sm" | "default" | "lg";
  showIcon?: boolean;
  className?: string;
}

export function PriceBadge({
  value,
  type = "percentage",
  size = "default",
  showIcon = true,
  className,
}: PriceBadgeProps) {
  const isPositive = value > 0;
  const isNeutral = value === 0;

  const formatted =
    type === "percentage" ? formatPercentage(value) : formatCurrency(Math.abs(value));

  const Icon = isNeutral ? Minus : isPositive ? TrendingUp : TrendingDown;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 font-mono font-medium tabular-nums",
        {
          "text-xs": size === "sm",
          "text-sm": size === "default",
          "text-base": size === "lg",
        },
        isNeutral
          ? "text-slate-500 dark:text-slate-400"
          : isPositive
          ? "text-emerald-600 dark:text-emerald-400"
          : "text-red-600 dark:text-red-400",
        className
      )}
    >
      {showIcon && <Icon className={cn(size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5")} />}
      {type === "currency" && !isNeutral && (isPositive ? "+" : "-")}
      {formatted}
    </span>
  );
}
