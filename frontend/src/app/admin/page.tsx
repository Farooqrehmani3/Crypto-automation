"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Shield,
  LogOut,
  TrendingUp,
  Users,
  Newspaper,
  BarChart3,
  Activity,
  Database,
} from "lucide-react";
import { useAdminAuth } from "@/hooks/useAdminAuth";
import { Button } from "@/components/ui/button";

const adminCards = [
  {
    title: "Market Overview",
    description: "View global market data, fear & greed index, and trends",
    icon: BarChart3,
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "User Management",
    description: "Manage registered users and their permissions",
    icon: Users,
    color: "from-purple-500 to-pink-500",
  },
  {
    title: "News & Sentiment",
    description: "Monitor AI-analyzed news articles and sentiment",
    icon: Newspaper,
    color: "from-green-500 to-emerald-500",
  },
  {
    title: "AI Predictions",
    description: "Review and manage AI-generated price predictions",
    icon: TrendingUp,
    color: "from-orange-500 to-red-500",
  },
  {
    title: "System Status",
    description: "Monitor API health, database connections, and workers",
    icon: Activity,
    color: "from-amber-500 to-yellow-500",
  },
  {
    title: "Database",
    description: "View database statistics and manage data",
    icon: Database,
    color: "from-sky-500 to-indigo-500",
  },
];

export default function AdminDashboard() {
  const router = useRouter();
  const { admin, isAuthenticated, isLoading, isInitialized, signOut } = useAdminAuth();

  useEffect(() => {
    if (isInitialized && !isLoading && !isAuthenticated) {
      router.replace("/admin/login");
    }
  }, [isInitialized, isLoading, isAuthenticated, router]);

  if (isLoading || !isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.02] pointer-events-none" />

      <div className="relative z-10">
        {/* Top Bar */}
        <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600">
                  <Shield className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-white">Admin Panel</h1>
                  <p className="text-xs text-slate-400">TecFlux AI Crypto Intelligence</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <span className="text-sm text-slate-400">
                  Signed in as{" "}
                  <span className="text-amber-400 font-medium">{admin?.username}</span>
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={signOut}
                  className="border-slate-700 text-slate-300 hover:text-white hover:border-slate-600 gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-xl font-semibold text-white mb-6">Admin Dashboard</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {adminCards.map((card, index) => (
                <motion.div
                  key={card.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="group relative rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-6 hover:border-slate-600/50 hover:bg-slate-800/70 transition-all duration-200 cursor-pointer"
                >
                  <div
                    className={`inline-flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} mb-4`}
                  >
                    <card.icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="text-base font-semibold text-white group-hover:text-amber-400 transition-colors">
                    {card.title}
                  </h3>
                  <p className="mt-1.5 text-sm text-slate-400 leading-relaxed">
                    {card.description}
                  </p>
                </motion.div>
              ))}
            </div>

            {/* Quick Stats */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-4">
                <p className="text-xs text-slate-400 uppercase tracking-wider">API Status</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
                  </span>
                  <span className="text-sm font-medium text-green-400">Operational</span>
                </div>
              </div>

              <div className="rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-4">
                <p className="text-xs text-slate-400 uppercase tracking-wider">Database</p>
                <p className="mt-2 text-sm font-medium text-white">Supabase PostgreSQL</p>
                <p className="text-xs text-slate-500 mt-0.5">Connected</p>
              </div>

              <div className="rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-4">
                <p className="text-xs text-slate-400 uppercase tracking-wider">AI Service</p>
                <p className="mt-2 text-sm font-medium text-white">OpenAI GPT-4o</p>
                <p className="text-xs text-slate-500 mt-0.5">Ready</p>
              </div>

              <div className="rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-4">
                <p className="text-xs text-slate-400 uppercase tracking-wider">Redis Cache</p>
                <p className="mt-2 text-sm font-medium text-white">Local Instance</p>
                <p className="text-xs text-slate-500 mt-0.5">Available</p>
              </div>
            </div>
          </motion.div>
        </main>
      </div>
    </div>
  );
}
