export type AnalysisStatus = "idle" | "pending" | "processing" | "completed" | "failed";
export type AgentType = "technical" | "sentiment" | "fundamental" | "onchain" | "macro";

export interface AnalysisResult {
  id: string;
  coinId: string;
  coinName: string;
  coinSymbol: string;
  agentOutputs: AgentOutput[];
  consolidatedForecast: Forecast;
  status: AnalysisStatus;
  requestedAt: string;
  completedAt: string | null;
  error: string | null;
}

export interface AgentOutput {
  agentId: string;
  agentType: AgentType;
  agentName: string;
  confidenceScore: number; // 0-100
  forecast: Forecast;
  reasoning: string;
  keyPoints: string[];
  dataPoints: AgentDataPoint[];
  generatedAt: string;
  processingTime: number; // ms
}

export interface Forecast {
  direction: "bullish" | "bearish" | "neutral";
  targetPrice: number | null;
  confidence: number; // 0-100
  timeframe: string;
  potentialReturn: number | null; // percentage
  riskLevel: "low" | "medium" | "high";
  supportLevels: number[];
  resistanceLevels: number[];
  summary: string;
}

export interface AgentDataPoint {
  label: string;
  value: number | string;
  change: number | null;
  changeType: "positive" | "negative" | "neutral";
  description: string;
}

export interface AnalysisRequest {
  coinId: string;
  agentTypes: AgentType[];
  analysisType: string;
}

export interface AnalysisPollResult {
  analysisId: string;
  status: AnalysisStatus;
  progress: number; // 0-100
  completedAgentCount: number;
  totalAgentCount: number;
  result: AnalysisResult | null;
}
