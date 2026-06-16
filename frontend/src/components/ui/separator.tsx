"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const separatorVariants = cva("shrink-0 bg-secondary-200 dark:bg-secondary-700", {
  variants: {
    orientation: {
      horizontal: "h-[1px] w-full",
      vertical: "h-full w-[1px]",
    },
    variant: {
      default: "",
      dashed: "bg-transparent bg-[repeating-linear-gradient(to_right,transparent,transparent_4px,currentColor_4px,currentColor_8px)] dark:bg-[repeating-linear-gradient(to_right,transparent,transparent_4px,currentColor_4px,currentColor_8px)]",
      dotted: "bg-transparent bg-[radial-gradient(circle,currentColor_1px,transparent_1px)] bg-[length:4px_4px] dark:bg-[radial-gradient(circle,currentColor_1px,transparent_1px)]",
    },
  },
  defaultVariants: {
    orientation: "horizontal",
    variant: "default",
  },
});

export interface SeparatorProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof separatorVariants> {
  decorative?: boolean;
  label?: string;
}

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  (
    { className, orientation = "horizontal", variant, decorative = true, label, ...props },
    ref
  ) => {
    if (label) {
      return (
        <div className="flex items-center gap-3" ref={ref}>
          <div
            className={cn(separatorVariants({ orientation, variant }), "flex-1", className)}
            {...(decorative ? {} : { role: "separator" })}
            {...props}
          />
          <span className="text-xs text-secondary-400 dark:text-secondary-500 font-medium shrink-0">
            {label}
          </span>
          <div
            className={cn(separatorVariants({ orientation, variant }), "flex-1", className)}
            {...(decorative ? {} : { role: "separator" })}
            {...props}
          />
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(separatorVariants({ orientation, variant, className }))}
        role={decorative ? "none" : "separator"}
        aria-orientation={decorative ? undefined : (orientation as "horizontal" | "vertical")}
        {...(props as React.HTMLAttributes<HTMLDivElement>)}
      />
    );
  }
);
Separator.displayName = "Separator";

export { Separator, separatorVariants };
