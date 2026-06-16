"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const progressVariants = cva(
  "relative h-2 w-full overflow-hidden rounded-full bg-secondary-200 dark:bg-secondary-700",
  {
    variants: {
      size: {
        sm: "h-1",
        default: "h-2",
        lg: "h-3",
        xl: "h-4",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
);

const indicatorVariants = cva("h-full rounded-full transition-all duration-500 ease-out", {
  variants: {
    variant: {
      default: "bg-gradient-to-r from-blue-500 to-blue-600",
      success: "bg-gradient-to-r from-green-500 to-emerald-500",
      warning: "bg-gradient-to-r from-yellow-500 to-orange-500",
      danger: "bg-gradient-to-r from-red-500 to-rose-500",
      purple: "bg-gradient-to-r from-purple-500 to-indigo-500",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export interface ProgressProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof progressVariants> {
  value?: number;
  max?: number;
  variant?: VariantProps<typeof indicatorVariants>["variant"];
  showLabel?: boolean;
  animated?: boolean;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  (
    {
      className,
      size,
      value = 0,
      max = 100,
      variant = "default",
      showLabel = false,
      animated = false,
      ...props
    },
    ref
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    return (
      <div className="w-full space-y-1.5">
        <div
          ref={ref}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={max}
          aria-valuenow={value}
          className={cn(progressVariants({ size, className }))}
          {...props}
        >
          <div
            className={cn(
              indicatorVariants({ variant }),
              animated && "animate-pulse"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showLabel && (
          <p className="text-xs text-secondary-500 dark:text-secondary-400">
            {Math.round(percentage)}%
          </p>
        )}
      </div>
    );
  }
);
Progress.displayName = "Progress";

export { Progress, progressVariants };
