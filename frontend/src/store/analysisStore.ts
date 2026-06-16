"use client";

import { create } from "zustand";
import type { AnalysisResult, AgentOutput, AnalysisStatus, AgentType } from "@/lib/types/analysis";

interface AnalysisState {
  // Active analysis
  activeAnalysisId: string | null;
  activeAnalysis: AnalysisResult | null;
  analysisStatus: AnalysisStatus;
  setActiveAnalysis: (analysis: AnalysisResult | null) => void;
  setAnalysisStatus: (status: AnalysisStatus) => void;

  // Agent tabs
  selectedAgentTab: AgentType;
  setSelectedAgentTab: (agentType: AgentType) => void;
  agentOutputs: AgentOutput[];
  setAgentOutputs: (outputs: AgentOutput[]) => void;
  addAgentOutput: (output: AgentOutput) => void;
  updateAgentOutput: (agentId: string, output: Partial<AgentOutput>) => void;

  // Polling
  isPolling: boolean;
  setIsPolling: (polling: boolean) => void;
  pollingInterval: number | null;
  setPollingInterval: (interval: number | null) => void;

  // Analysis history
  analysisHistory: AnalysisResult[];
  setAnalysisHistory: (history: AnalysisResult[]) => void;
  addToHistory: (analysis: AnalysisResult) => void;
}

export const useAnalysisStore = create<AnalysisState>()((set) => ({
  // Active analysis
  activeAnalysisId: null,
  activeAnalysis: null,
  analysisStatus: "idle",
  setActiveAnalysis: (analysis) =>
    set({
      activeAnalysis: analysis,
      activeAnalysisId: analysis?.id ?? null,
    }),
  setAnalysisStatus: (status) => set({ analysisStatus: status }),

  // Agent tabs
  selectedAgentTab: "technical",
  setSelectedAgentTab: (agentType) => set({ selectedAgentTab: agentType }),
  agentOutputs: [],
  setAgentOutputs: (outputs) => set({ agentOutputs: outputs }),
  addAgentOutput: (output) =>
    set((state) => ({
      agentOutputs: [...state.agentOutputs, output],
    })),
  updateAgentOutput: (agentId, output) =>
    set((state) => ({
      agentOutputs: state.agentOutputs.map((a) =>
        a.agentId === agentId ? { ...a, ...output } : a
      ),
    })),

  // Polling
  isPolling: false,
  setIsPolling: (polling) => set({ isPolling: polling }),
  pollingInterval: null,
  setPollingInterval: (interval) => set({ pollingInterval: interval }),

  // Analysis history
  analysisHistory: [],
  setAnalysisHistory: (history) => set({ analysisHistory: history }),
  addToHistory: (analysis) =>
    set((state) => ({
      analysisHistory: [analysis, ...state.analysisHistory].slice(0, 50),
    })),
}));
