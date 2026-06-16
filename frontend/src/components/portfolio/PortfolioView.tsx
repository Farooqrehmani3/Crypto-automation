"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, DollarSign, PieChart, Plus, ArrowUpRight, ArrowDownRight, Trash2, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/shared/EmptyState";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { formatCurrency } from "@/lib/utils/formatters";

interface Holding {
  id: string;
  coinId: string;
  name: string;
  symbol: string;
  quantity: number;
  avgBuyPrice: number;
}

const COINGECKO_BASE = "https://api.coingecko.com/api/v3";
const DEMO_API_KEY = "CG-fUUVXcpZGgijdkEfJuyU9cU4";

export function PortfolioView() {
  const [holdings, setHoldings] = useLocalStorage<Holding[]>("portfolio-holdings", []);
  const [prices, setPrices] = useState<Record<string, number>>({});
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ coinId: "", name: "", symbol: "", quantity: "", avgBuyPrice: "" });
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Fetch live prices for all holdings
  useEffect(() => {
    if (holdings.length === 0) return;
    const ids = holdings.map((h) => h.coinId).join(",");
    fetch(`${COINGECKO_BASE}/simple/price?vs_currencies=usd&ids=${ids}&x_cg_demo_api_key=${DEMO_API_KEY}`)
      .then((r) => r.json())
      .then((data) => {
        const p: Record<string, number> = {};
        for (const h of holdings) {
          p[h.id] = data[h.coinId]?.usd ?? 0;
        }
        setPrices(p);
      })
      .catch(() => {});
  }, [holdings]);

  // Search coins for add form
  const searchCoins = async (query: string) => {
    if (query.length < 2) { setSearchResults([]); return; }
    setSearching(true);
    try {
      const res = await fetch(`${COINGECKO_BASE}/search?query=${encodeURIComponent(query)}&x_cg_demo_api_key=${DEMO_API_KEY}`);
      const data = await res.json();
      setSearchResults(data.coins?.slice(0, 8) || []);
    } catch { setSearchResults([]); }
    finally { setSearching(false); }
  };

  const addHolding = (coin: any) => {
    setForm({
      coinId: coin.id,
      name: coin.name,
      symbol: coin.symbol?.toUpperCase() || "",
      quantity: "1",
      avgBuyPrice: "",
    });
    setSearchResults([]);
  };

  const saveHolding = () => {
    const qty = parseFloat(form.quantity);
    const price = parseFloat(form.avgBuyPrice);
    if (!form.coinId || !form.name || isNaN(qty) || qty <= 0 || isNaN(price) || price <= 0) return;

    setHoldings([
      ...holdings,
      {
        id: `${form.coinId}-${Date.now()}`,
        coinId: form.coinId,
        name: form.name,
        symbol: form.symbol || form.coinId.toUpperCase(),
        quantity: qty,
        avgBuyPrice: price,
      },
    ]);
    setShowForm(false);
    setForm({ coinId: "", name: "", symbol: "", quantity: "", avgBuyPrice: "" });
  };

  const removeHolding = (id: string) => {
    setHoldings(holdings.filter((h) => h.id !== id));
  };

  // Compute totals
  const holdingsWithValue = holdings.map((h) => {
    const currentPrice = prices[h.id] || 0;
    const value = h.quantity * currentPrice;
    const cost = h.quantity * h.avgBuyPrice;
    const pnl = value - cost;
    const pnlPct = cost > 0 ? (pnl / cost) * 100 : 0;
    return { ...h, currentPrice, value, cost, pnl, pnlPct };
  });

  const totalValue = holdingsWithValue.reduce((s, h) => s + h.value, 0);
  const totalCost = holdingsWithValue.reduce((s, h) => s + h.cost, 0);
  const totalPnl = totalValue - totalCost;
  const totalPnlPct = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;

  if (holdings.length === 0 && !showForm) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <EmptyState
          icon={PieChart}
          title="No portfolio yet"
          description="Track your cryptocurrency holdings. Add your first asset to see portfolio value, profit/loss, and allocation."
          action={{
            label: "Add Asset",
            onClick: () => setShowForm(true),
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white sm:text-3xl">Portfolio</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {holdings.length === 0 ? "Track your crypto holdings" : `${holdings.length} asset${holdings.length > 1 ? "s" : ""} tracked`}
          </p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowForm(!showForm)}>
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? "Cancel" : "Add Asset"}
        </Button>
      </div>

      {/* Add Asset Form */}
      {showForm && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-5">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Add New Holding</h3>

            {/* Search */}
            {!form.coinId ? (
              <div className="space-y-3">
                <Input
                  placeholder="Search for a coin (e.g. bitcoin, ethereum)..."
                  onChange={(e) => searchCoins(e.target.value)}
                />
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {searchResults.map((coin: any) => (
                    <button
                      key={coin.id}
                      onClick={() => addHolding(coin)}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-left transition-colors"
                    >
                      {coin.thumb && <img src={coin.thumb} alt="" className="w-6 h-6 rounded-full" />}
                      <div>
                        <p className="text-sm font-medium text-slate-900 dark:text-white">{coin.name}</p>
                        <p className="text-xs text-slate-500 uppercase">{coin.symbol}</p>
                      </div>
                    </button>
                  ))}
                  {searchResults.length === 0 && !searching && (
                    <p className="text-xs text-slate-400 text-center py-2">Type to search coins</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <span className="text-sm font-medium text-slate-900 dark:text-white">{form.name} ({form.symbol})</span>
                  <button onClick={() => setForm({ coinId: "", name: "", symbol: "", quantity: "", avgBuyPrice: "" })} className="text-xs text-blue-500 hover:underline">Change</button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Quantity</label>
                    <Input
                      type="number"
                      step="any"
                      min="0"
                      placeholder="0.5"
                      value={form.quantity}
                      onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 mb-1 block">Avg Buy Price (USD)</label>
                    <Input
                      type="number"
                      step="any"
                      min="0"
                      placeholder="42000"
                      value={form.avgBuyPrice}
                      onChange={(e) => setForm({ ...form, avgBuyPrice: e.target.value })}
                    />
                  </div>
                </div>
                <Button onClick={saveHolding} className="w-full" disabled={!form.quantity || !form.avgBuyPrice}>
                  Add to Portfolio
                </Button>
              </div>
            )}
          </Card>
        </motion.div>
      )}

      {/* Summary Cards — only show if holdings exist */}
      {holdings.length > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-5">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Value</p>
              <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white tabular-nums">{formatCurrency(totalValue)}</p>
            </Card>
            <Card className="p-5">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Cost</p>
              <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white tabular-nums">{formatCurrency(totalCost)}</p>
            </Card>
            <Card className="p-5">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Profit/Loss</p>
              <div className="flex items-center gap-1.5 mt-1">
                {totalPnl >= 0 ? <ArrowUpRight className="h-5 w-5 text-emerald-500" /> : <ArrowDownRight className="h-5 w-5 text-red-500" />}
                <p className={`text-2xl font-bold tabular-nums ${totalPnl >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                  {formatCurrency(Math.abs(totalPnl))}
                </p>
              </div>
            </Card>
            <Card className="p-5">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Return</p>
              <div className="flex items-center gap-1.5 mt-1">
                {totalPnlPct >= 0 ? <TrendingUp className="h-5 w-5 text-emerald-500" /> : <TrendingDown className="h-5 w-5 text-red-500" />}
                <p className={`text-2xl font-bold tabular-nums ${totalPnlPct >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                  {totalPnlPct >= 0 ? "+" : ""}{totalPnlPct.toFixed(2)}%
                </p>
              </div>
            </Card>
          </div>

          {/* Holdings Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800">
                    <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Asset</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Qty</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase hidden sm:table-cell">Avg Buy</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Value</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">P&L</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {holdingsWithValue.map((h) => (
                    <tr key={h.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="h-7 w-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                            {h.symbol.charAt(0)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-900 dark:text-white">{h.name}</p>
                            <p className="text-xs text-slate-500">{h.symbol}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-slate-900 dark:text-white font-medium tabular-nums">{h.quantity}</td>
                      <td className="px-4 py-3 text-sm text-right text-slate-500 hidden sm:table-cell tabular-nums">{formatCurrency(h.avgBuyPrice)}</td>
                      <td className="px-4 py-3 text-sm text-right text-slate-900 dark:text-white font-medium tabular-nums">{formatCurrency(h.currentPrice)}</td>
                      <td className="px-4 py-3 text-sm text-right text-slate-900 dark:text-white font-medium tabular-nums">{formatCurrency(h.value)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <span className={`text-sm font-medium tabular-nums ${h.pnl >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                            {h.pnlPct >= 0 ? "+" : ""}{h.pnlPct.toFixed(2)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button onClick={() => removeHolding(h.id)} className="text-slate-400 hover:text-red-500 transition-colors">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
