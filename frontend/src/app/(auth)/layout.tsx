import type { Metadata } from "next";
import Link from "next/link";
import { TrendingUp } from "lucide-react";

export const metadata: Metadata = {
  title: {
    default: "Authentication",
    template: "%s | TecFlux",
  },
  robots: {
    index: false,
    follow: false,
  },
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-gradient-to-br from-secondary-50 via-white to-blue-50 dark:from-secondary-950 dark:via-secondary-950 dark:to-blue-950">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-purple-500/10 blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-blue-500/5 to-purple-500/5 blur-3xl" />
      </div>

      {/* Logo */}
      <div className="relative mb-8">
        <Link href="/" className="inline-flex items-center gap-3 group">
          <img src="/images/logo/tf.jpg" alt="TecFlux" className="h-10 w-10 rounded-xl object-cover shadow-lg shadow-blue-500/25 transition-transform group-hover:scale-105" />
          <span className="text-xl font-bold text-secondary-900 dark:text-white">
            TecFlux
          </span>
        </Link>
      </div>

      {/* Auth Card Container */}
      <div className="relative w-full max-w-md">
        <div className="glass-card p-8 sm:p-10">{children}</div>
      </div>

      {/* Footer */}
      <div className="relative mt-8 text-center text-xs text-secondary-400">
        <p>
          By continuing, you agree to our{" "}
          <Link href="/terms" className="underline hover:text-secondary-500">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="/privacy" className="underline hover:text-secondary-500">
            Privacy Policy
          </Link>
        </p>
      </div>
    </div>
  );
}
