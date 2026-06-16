"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { LucideIcon } from "lucide-react";
import { PackageOpen } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: LucideIcon;
  };
  className?: string;
  size?: "sm" | "default" | "lg";
}

export function EmptyState({
  icon: Icon = PackageOpen,
  title,
  description,
  action,
  className,
  size = "default",
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        className={cn(
          "flex flex-col items-center justify-center text-center mx-auto",
          {
            "p-4 space-y-2 max-w-xs": size === "sm",
            "p-8 space-y-4 max-w-md": size === "default",
            "p-12 space-y-6 max-w-lg": size === "lg",
          },
          className
        )}
      >
        <div
          className={cn(
            "rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center",
            {
              "w-10 h-10": size === "sm",
              "w-14 h-14": size === "default",
              "w-20 h-20": size === "lg",
            }
          )}
        >
          <Icon
            className={cn("text-slate-400 dark:text-slate-500", {
              "w-5 h-5": size === "sm",
              "w-7 h-7": size === "default",
              "w-10 h-10": size === "lg",
            })}
          />
        </div>

        <div>
          <h3
            className={cn("font-semibold text-slate-900 dark:text-white", {
              "text-sm": size === "sm",
              "text-base": size === "default",
              "text-lg": size === "lg",
            })}
          >
            {title}
          </h3>
          {description && (
            <p
              className={cn("text-slate-500 dark:text-slate-400 mt-1", {
                "text-xs": size === "sm",
                "text-sm": size === "default",
              })}
            >
              {description}
            </p>
          )}
        </div>

        {action && (
          <Button
            variant={size === "sm" ? "outline" : "default"}
            size={size === "sm" ? "sm" : "default"}
            onClick={action.onClick}
            className="gap-2"
          >
            {action.icon && <action.icon className="w-4 h-4" />}
            {action.label}
          </Button>
        )}
      </Card>
    </motion.div>
  );
}
