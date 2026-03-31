/**
 * RepoLens 分析状态 Store (Zustand)
 */
import { create } from "zustand";

interface AnalysisState {
  analysisId: string | null;
  status: string; // idle / pending / fetching / indexing / analyzing / done / failed
  progress: number; // 0-100
  currentStep: string;
  error: string | null;

  // Actions
  setAnalysisId: (id: string) => void;
  setStatus: (status: string) => void;
  setProgress: (progress: number) => void;
  setCurrentStep: (step: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  analysisId: null,
  status: "idle",
  progress: 0,
  currentStep: "",
  error: null,

  setAnalysisId: (id) => set({ analysisId: id }),
  setStatus: (status) => set({ status }),
  setProgress: (progress) => set({ progress }),
  setCurrentStep: (step) => set({ currentStep: step }),
  setError: (error) => set({ error }),
  reset: () =>
    set({
      analysisId: null,
      status: "idle",
      progress: 0,
      currentStep: "",
      error: null,
    }),
}));
