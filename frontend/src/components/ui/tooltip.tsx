"use client";

import * as React from "react";
import { cn } from "@/lib/utils/cn";

interface TooltipContextValue {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  triggerRef: React.RefObject<HTMLDivElement | null>;
}

const TooltipContext = React.createContext<TooltipContextValue | null>(null);

function useTooltipContext() {
  const context = React.useContext(TooltipContext);
  if (!context) {
    throw new Error("Tooltip components must be used within a TooltipProvider");
  }
  return context;
}

interface TooltipProviderProps {
  children: React.ReactNode;
  delayDuration?: number;
}

function TooltipProvider({ children, delayDuration = 300 }: TooltipProviderProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const triggerRef = React.useRef<HTMLDivElement>(null!);
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = React.useCallback(() => {
    timeoutRef.current = setTimeout(() => setIsOpen(true), delayDuration);
  }, [delayDuration]);

  const handleMouseLeave = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsOpen(false);
  }, []);

  return (
    <TooltipContext.Provider value={{ isOpen, setIsOpen, triggerRef }}>
      <div
        className="relative inline-block"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {children}
      </div>
    </TooltipContext.Provider>
  );
}

interface TooltipTriggerProps extends React.HTMLAttributes<HTMLDivElement> {
  asChild?: boolean;
}

const TooltipTrigger = React.forwardRef<HTMLDivElement, TooltipTriggerProps>(
  ({ className, asChild, children, ...props }, ref) => {
    const { triggerRef } = useTooltipContext();

    return (
      <div
        ref={(node) => {
          triggerRef.current = node!;
          if (typeof ref === "function") ref(node);
          else if (ref) ref.current = node;
        }}
        className={cn("inline-block", className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);
TooltipTrigger.displayName = "TooltipTrigger";

interface TooltipContentProps extends React.HTMLAttributes<HTMLDivElement> {
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
  sideOffset?: number;
}

const TooltipContent = React.forwardRef<HTMLDivElement, TooltipContentProps>(
  (
    { className, side = "top", align = "center", sideOffset = 4, children, ...props },
    ref
  ) => {
    const { isOpen } = useTooltipContext();

    if (!isOpen) return null;

    const sideStyles = {
      top: "bottom-full left-1/2 -translate-x-1/2",
      bottom: "top-full left-1/2 -translate-x-1/2",
      left: "right-full top-1/2 -translate-y-1/2",
      right: "left-full top-1/2 -translate-y-1/2",
    };

    const marginStyles = {
      top: { marginBottom: sideOffset },
      bottom: { marginTop: sideOffset },
      left: { marginRight: sideOffset },
      right: { marginLeft: sideOffset },
    };

    return (
      <div
        ref={ref}
        role="tooltip"
        className={cn(
          "absolute z-50 animate-scale-in rounded-lg px-3 py-1.5 text-xs font-medium",
          "bg-secondary-900 text-white shadow-lg dark:bg-white dark:text-secondary-900",
          sideStyles[side],
          className
        )}
        style={marginStyles[side]}
        {...props}
      >
        {children}
      </div>
    );
  }
);
TooltipContent.displayName = "TooltipContent";

export { TooltipProvider, TooltipTrigger, TooltipContent };
