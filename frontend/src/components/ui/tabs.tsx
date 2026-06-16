"use client";

import { cn } from "@/lib/utils/cn";

interface TabsProps {
  tabs: { id: string; label: string; count?: number; icon?: React.ReactNode }[];
  activeTab: string;
  onChange: (tabId: string) => void;
  variant?: "underline" | "pills" | "buttons";
  className?: string;
}

export function Tabs({
  tabs,
  activeTab,
  onChange,
  variant = "underline",
  className,
}: TabsProps) {
  return (
    <div
      className={cn(
        "flex gap-1",
        variant === "underline" && "border-b border-slate-200 dark:border-slate-800",
        variant === "pills" && "bg-slate-100 dark:bg-slate-800 rounded-xl p-1",
        variant === "buttons" && "gap-2",
        className
      )}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;

        const baseClasses = "relative flex items-center gap-1.5 text-sm font-medium transition-all duration-200 whitespace-nowrap";

        const variantClasses = (() => {
          switch (variant) {
            case "underline":
              return cn(
                "px-4 py-2.5 -mb-[1px]",
                !isActive && "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200",
                isActive && "text-blue-600 dark:text-blue-400 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600 dark:after:bg-blue-400 after:rounded-full"
              );
            case "pills":
              return cn(
                "px-3 py-1.5 rounded-lg",
                !isActive && "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200",
                isActive && "text-slate-900 dark:text-white bg-white dark:bg-slate-700 shadow-sm"
              );
            case "buttons":
              return cn(
                "px-4 py-2 rounded-xl border",
                !isActive && "border-slate-200 dark:border-slate-700 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800",
                isActive && "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300"
              );
          }
        })();

        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(baseClasses, variantClasses)}
          >
            {tab.icon}
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={cn(
                  "ml-1 px-1.5 py-0.5 rounded-full text-xs",
                  isActive
                    ? "bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
