export type ContractLanguage = 'solidity' | 'vyper' | 'move';
export type AuditStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type VulnerabilitySeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type ReportFormat = 'pdf' | 'json' | 'html' | 'markdown';

export interface ContractFile {
  name: string;
  content: string;
}

export interface AuditRequest {
  code: string;
  language: ContractLanguage;
  compiler_version?: string;
  optimization_enabled?: boolean;
  files?: ContractFile[];
}

export interface AuditResponse {
  audit_id: string;
  status: AuditStatus;
  estimated_time: number;
  message: string;
}

export interface LocationInfo {
  file?: string;
  line?: number;
  function?: string;
}

export interface VulnerabilityDetail {
  id: string;
  title: string;
  severity: VulnerabilitySeverity;
  exploitability?: string;
  category?: string;
  location: LocationInfo;
  description: string;
  exploit_scenario?: string;
  recommendation?: string;
  fixed_code?: string;
  code_snippet?: string;
  cwe_id?: string;
  swc_id?: string;
  references?: string[];
  detected_by?: string;
  confidence: number;
}

export interface GasOptimization {
  issue: string;
  line?: number;
  current_cost?: string;
  optimized_cost?: string;
  savings?: string;
  recommendation: string;
}

export interface GasAnalysisResult {
  total_estimated_gas?: number;
  optimizations: GasOptimization[];
  potential_savings?: string;
}

export interface ContractInfo {
  language: string;
  compiler_version?: string;
  contract_name?: string;
  total_lines: number;
}

export interface AIAnalysis {
  summary?: string;
  overall_risk?: string;
  architectural_issues?: string[];
  logic_flaws?: string[];
  best_practice_violations?: string[];
}

export interface AuditResult {
  audit_id: string;
  status: AuditStatus;
  created_at: string;
  completed_at?: string;
  processing_time_seconds?: number;
  contract_info: ContractInfo;
  vulnerabilities: VulnerabilityDetail[];
  vulnerability_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  risk_score: number;
  security_rating?: string;
  gas_analysis?: GasAnalysisResult;
  ai_analysis?: AIAnalysis;
  recommendations?: string[];
  error_message?: string;
}

export interface ReportRequest {
  audit_id: string;
  format: ReportFormat;
  options?: {
    include_code_snippets?: boolean;
    include_gas_analysis?: boolean;
    include_ai_insights?: boolean;
    include_recommendations?: boolean;
    include_executive_summary?: boolean;
  };
}

export interface ReportResponse {
  report_id: string;
  audit_id: string;
  format: ReportFormat;
  file_name: string;
  file_size_bytes?: number;
  download_url: string;
  created_at: string;
  share_token?: string;
}
