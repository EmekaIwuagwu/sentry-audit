import { create } from 'zustand';
import type { AuditResult, ContractLanguage } from '@/types';

interface AuditStore {
  // Current audit state
  currentCode: string;
  language: ContractLanguage;
  compilerVersion: string;
  optimizationEnabled: boolean;

  // Audit results
  currentAuditId: string | null;
  auditResult: AuditResult | null;
  isLoading: boolean;
  error: string | null;

  // History
  auditHistory: AuditResult[];

  // Actions
  setCode: (code: string) => void;
  setLanguage: (language: ContractLanguage) => void;
  setCompilerVersion: (version: string) => void;
  setOptimizationEnabled: (enabled: boolean) => void;
  setCurrentAuditId: (id: string | null) => void;
  setAuditResult: (result: AuditResult | null) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addToHistory: (result: AuditResult) => void;
  clearAudit: () => void;
}

export const useAuditStore = create<AuditStore>((set) => ({
  // Initial state
  currentCode: '',
  language: 'solidity',
  compilerVersion: '0.8.20',
  optimizationEnabled: false,
  currentAuditId: null,
  auditResult: null,
  isLoading: false,
  error: null,
  auditHistory: [],

  // Actions
  setCode: (code) => set({ currentCode: code }),
  setLanguage: (language) => set({ language }),
  setCompilerVersion: (version) => set({ compilerVersion: version }),
  setOptimizationEnabled: (enabled) => set({ optimizationEnabled: enabled }),
  setCurrentAuditId: (id) => set({ currentAuditId: id }),
  setAuditResult: (result) => set({ auditResult: result }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  addToHistory: (result) => set((state) => ({
    auditHistory: [result, ...state.auditHistory].slice(0, 20), // Keep last 20
  })),
  clearAudit: () => set({
    currentAuditId: null,
    auditResult: null,
    error: null,
  }),
}));
