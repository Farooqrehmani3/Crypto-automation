export interface PortfolioAsset {
  id: string;
  coinId: string;
  coinName: string;
  coinSymbol: string;
  image: string;
  quantity: number;
  averageBuyPrice: number;
  currentPrice: number;
  totalValue: number;
  totalCost: number;
  profitLoss: number;
  profitLossPercentage: number;
  allocation: number; // percentage of portfolio
  lastUpdated: string;
}

export interface Portfolio {
  id: string;
  userId: string;
  name: string;
  description: string;
  assets: PortfolioAsset[];
  totalValue: number;
  totalCost: number;
  totalProfitLoss: number;
  totalProfitLossPercentage: number;
  allocationByAsset: AllocationData[];
  createdAt: string;
  updatedAt: string;
}

export interface PortfolioTransaction {
  id: string;
  portfolioAssetId: string;
  coinId: string;
  coinName: string;
  coinSymbol: string;
  type: "buy" | "sell" | "transfer_in" | "transfer_out";
  quantity: number;
  pricePerUnit: number;
  totalValue: number;
  fee: number;
  notes: string | null;
  transactionDate: string;
  createdAt: string;
}

export interface PerformancePoint {
  date: string;
  value: number;
  profitLoss: number;
  profitLossPercentage: number;
}

export interface AllocationData {
  coinId: string;
  coinName: string;
  coinSymbol: string;
  value: number;
  percentage: number;
  color: string;
}
