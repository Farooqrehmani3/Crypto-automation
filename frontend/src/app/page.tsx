"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, TrendingUp, Shield, Zap, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: TrendingUp,
    title: "AI-Powered Predictions",
    description: "Get institutional-grade forecasts powered by advanced machine learning models analyzing millions of data points in real-time.",
  },
  {
    icon: Shield,
    title: "Multi-Agent Analysis",
    description: "Our specialized AI agents analyze technical, sentiment, fundamental, on-chain, and macro factors simultaneously.",
  },
  {
    icon: Zap,
    title: "Real-Time Intelligence",
    description: "Stay ahead with sub-second data updates, instant alerts, and live market monitoring across thousands of cryptocurrencies.",
  },
  {
    icon: BarChart3,
    title: "Portfolio Analytics",
    description: "Track performance, analyze risk metrics, and receive AI-optimized rebalancing suggestions for your crypto portfolio.",
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
};

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white dark:bg-secondary-950">
      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-secondary-200/50 dark:border-secondary-800/50">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <img src="/images/logo/tf.jpg" alt="TecFlux Logo" className="h-10 w-10 rounded-lg object-cover" />
              <span className="text-lg font-bold text-secondary-900 dark:text-white">
                TecFlux
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 sm:pt-40 sm:pb-28">
        {/* Background gradient */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-cyan-500/20 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/50 px-4 py-1.5"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
              <span className="text-xs font-medium text-blue-700 dark:text-blue-300">
                AI Agents Now Live
              </span>
            </motion.div>

            <h1 className="text-4xl font-bold tracking-tight text-secondary-900 dark:text-white sm:text-6xl lg:text-7xl">
              Predict the Future of
              <span className="mt-2 block text-gradient">Crypto Markets</span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg text-secondary-600 dark:text-secondary-400 sm:text-xl">
              Harness the power of specialized AI agents that analyze technical patterns,
              market sentiment, on-chain data, and macroeconomics to generate institutional-grade
              crypto predictions.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/register">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg shadow-blue-500/25 px-8 h-14 text-base"
                >
                  Start Free Analysis
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" size="lg" className="h-14 px-8 text-base">
                  View Live Demo
                </Button>
              </Link>
            </div>

            <motion.p
              className="mt-4 text-sm text-secondary-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              No credit card required. Free tier includes 5 analyses per day.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-secondary-50 dark:bg-secondary-900/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            {...fadeInUp}
          >
            <h2 className="text-3xl font-bold text-secondary-900 dark:text-white sm:text-4xl">
              Powered by Advanced AI
            </h2>
            <p className="mt-4 text-lg text-secondary-500 dark:text-secondary-400">
              Our platform combines multiple specialized AI models for comprehensive market analysis
            </p>
          </motion.div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="glass-card p-6 hover:shadow-xl transition-shadow duration-300"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-600/10">
                  <feature.icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-secondary-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-sm text-secondary-500 dark:text-secondary-400 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            className="glass-card relative overflow-hidden p-8 sm:p-12 text-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-600/10" />
            <div className="relative">
              <h2 className="text-3xl font-bold text-secondary-900 dark:text-white sm:text-4xl">
                Ready to Transform Your Crypto Strategy?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-secondary-500 dark:text-secondary-400">
                Join thousands of traders and investors who use TecFlux to make
                data-driven decisions.
              </p>
              <div className="mt-8">
                <Link href="/register">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg shadow-blue-500/25 px-8 h-14"
                  >
                    Get Started Free
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-secondary-200 dark:border-secondary-800 bg-secondary-50 dark:bg-secondary-900/50">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm font-medium text-secondary-500 dark:text-secondary-400">
                TecFlux
              </span>
            </div>
            <p className="text-sm text-secondary-400">
              &copy; {new Date().getFullYear()} TecFlux. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
