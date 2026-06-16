"use client";

import Link from "next/link";
import { TrendingUp, Github, Twitter, MessageCircle } from "lucide-react";

const footerLinks = {
  product: {
    label: "Product",
    links: [
      { label: "Dashboard", href: "/dashboard" },
      { label: "Watchlist", href: "/watchlist" },
      { label: "Portfolio", href: "/portfolio" },
      { label: "Pricing", href: "/pricing" },
    ],
  },
  resources: {
    label: "Resources",
    links: [
      { label: "Documentation", href: "/docs" },
      { label: "API Reference", href: "/api-docs" },
      { label: "Blog", href: "/blog" },
      { label: "Help Center", href: "/help" },
    ],
  },
  company: {
    label: "Company",
    links: [
      { label: "About Us", href: "/about" },
      { label: "Contact", href: "/contact" },
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms of Service", href: "/terms" },
    ],
  },
};

export function Footer() {
  return (
    <footer className="border-t border-secondary-200 dark:border-secondary-800 bg-white/50 dark:bg-secondary-950/50 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="inline-flex items-center gap-2 group">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center transition-transform group-hover:scale-105">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <span className="text-base font-bold text-secondary-900 dark:text-white">
                TecFlux
              </span>
            </Link>
            <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400 max-w-xs leading-relaxed">
              AI-powered cryptocurrency analytics platform. Make smarter decisions with
              institutional-grade predictions and real-time market intelligence.
            </p>
            <div className="mt-4 flex items-center gap-3">
              <a
                href="https://twitter.com/cryptointel_ai"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800 text-secondary-500 dark:text-secondary-400 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
              >
                <Twitter className="h-4 w-4" />
              </a>
              <a
                href="https://github.com/crypto-intelligence-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800 text-secondary-500 dark:text-secondary-400 hover:text-secondary-900 dark:hover:text-white transition-colors"
              >
                <Github className="h-4 w-4" />
              </a>
              <a
                href="https://discord.gg/cryptointelai"
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800 text-secondary-500 dark:text-secondary-400 hover:text-indigo-500 dark:hover:text-indigo-400 transition-colors"
              >
                <MessageCircle className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Link groups */}
          {Object.values(footerLinks).map((group) => (
            <div key={group.label}>
              <h3 className="text-xs font-semibold text-secondary-900 dark:text-white uppercase tracking-wider">
                {group.label}
              </h3>
              <ul className="mt-4 space-y-3">
                {group.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-secondary-500 dark:text-secondary-400 hover:text-secondary-900 dark:hover:text-white transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-10 pt-6 border-t border-secondary-200 dark:border-secondary-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-secondary-400">
            &copy; {new Date().getFullYear()} TecFlux. All rights reserved.
          </p>
          <p className="text-xs text-secondary-400">
            Not financial advice. Crypto investments carry risk.
          </p>
        </div>
      </div>
    </footer>
  );
}
