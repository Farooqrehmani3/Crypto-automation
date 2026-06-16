"use client";

import * as React from "react";
import { cn } from "@/lib/utils/cn";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "glass" | "gradient" | "bordered";
  hover?: "none" | "lift" | "glow" | "scale";
  padding?: "none" | "sm" | "default" | "lg";
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = "default",
      hover = "none",
      padding = "default",
      children,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-2xl transition-all duration-300",
          {
            // Variants
            "bg-white shadow-sm border border-slate-200/60 dark:bg-slate-900 dark:border-slate-800/60":
              variant === "default",
            "bg-white/70 backdrop-blur-xl border border-white/20 shadow-xl dark:bg-slate-900/70 dark:border-slate-700/20":
              variant === "glass",
            "bg-gradient-to-br from-white via-blue-50/50 to-white shadow-lg border border-blue-100/50 dark:from-slate-900 dark:via-blue-950/20 dark:to-slate-900 dark:border-blue-900/30":
              variant === "gradient",
            "bg-white border-2 border-slate-100 shadow-none dark:bg-slate-900 dark:border-slate-800":
              variant === "bordered",

            // Hover effects
            "hover:shadow-md": hover === "lift",
            "hover:shadow-xl hover:shadow-blue-500/10 hover:border-blue-300/50 dark:hover:border-blue-700/50":
              hover === "glow",
            "hover:scale-[1.02]": hover === "scale",

            // Padding
            "p-0": padding === "none",
            "p-3": padding === "sm",
            "p-5": padding === "default",
            "p-7": padding === "lg",
          },
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = "Card";

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  spacing?: "default" | "tight";
}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, spacing = "default", ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "flex flex-col",
        spacing === "default" ? "space-y-1.5" : "space-y-0.5",
        className
      )}
      {...props}
    />
  )
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight text-slate-900 dark:text-slate-100",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn(
      "text-sm text-slate-500 dark:text-slate-400",
      className
    )}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-5 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex items-center p-5 pt-0 border-t border-slate-100 dark:border-slate-800 mt-4",
      className
    )}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
};
