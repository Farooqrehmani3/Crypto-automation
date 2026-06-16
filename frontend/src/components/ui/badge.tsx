"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
        primary:
          "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
        success:
          "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
        warning:
          "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
        danger:
          "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
        bullish:
          "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
        bearish:
          "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
        neutral:
          "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
        outline:
          "border border-slate-200 text-slate-600 bg-transparent dark:border-slate-700 dark:text-slate-400",
        gradient:
          "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm",
      },
      size: {
        default: "px-2.5 py-0.5 text-xs",
        sm: "px-2 py-0.5 text-[10px]",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  showIcon?: boolean;
  changeValue?: number;
}

function Badge({
  className,
  variant,
  size,
  showIcon = false,
  changeValue,
  children,
  ...props
}: BadgeProps) {
  const getIcon = () => {
    if (!showIcon && changeValue === undefined) return null;
    const val = changeValue ?? 0;
    if (val > 0) return <TrendingUp className="h-3 w-3" />;
    if (val < 0) return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  return (
    <div
      className={cn(badgeVariants({ variant, size }), className)}
      {...props}
    >
      {getIcon()}
      {children}
    </div>
  );
}

export { Badge, badgeVariants };
