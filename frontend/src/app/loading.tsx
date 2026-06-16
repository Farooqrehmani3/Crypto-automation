import { Loader2 } from "lucide-react";

export default function GlobalLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white dark:bg-secondary-950">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center animate-pulse-glow">
            <Loader2 className="h-8 w-8 text-white animate-spin-slow" />
          </div>
        </div>
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm font-medium text-secondary-600 dark:text-secondary-400">
            Loading
          </p>
          <div className="flex gap-1">
            <div
              className="h-2 w-2 rounded-full bg-blue-500 animate-bounce"
              style={{ animationDelay: "0ms" }}
            />
            <div
              className="h-2 w-2 rounded-full bg-blue-500 animate-bounce"
              style={{ animationDelay: "150ms" }}
            />
            <div
              className="h-2 w-2 rounded-full bg-blue-500 animate-bounce"
              style={{ animationDelay: "300ms" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
