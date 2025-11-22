import axios from 'axios';
import type {
  AuditRequest,
  AuditResponse,
  AuditResult,
  ReportRequest,
  ReportResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  health: async () => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },

  // Create audit
  createAudit: async (request: AuditRequest): Promise<AuditResponse> => {
    const response = await apiClient.post<AuditResponse>('/api/v1/audit', request);
    return response.data;
  },

  // Get audit result
  getAudit: async (auditId: string): Promise<AuditResult> => {
    const response = await apiClient.get<AuditResult>(`/api/v1/audit/${auditId}`);
    return response.data;
  },

  // List audits
  listAudits: async (skip = 0, limit = 50) => {
    const response = await apiClient.get('/api/v1/audits', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Delete audit
  deleteAudit: async (auditId: string) => {
    const response = await apiClient.delete(`/api/v1/audit/${auditId}`);
    return response.data;
  },

  // Generate report
  generateReport: async (request: ReportRequest): Promise<ReportResponse> => {
    const response = await apiClient.post<ReportResponse>(
      '/api/v1/report/generate',
      request
    );
    return response.data;
  },

  // Download report
  downloadReport: async (reportId: string): Promise<Blob> => {
    const response = await apiClient.get(`/api/v1/report/${reportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get report metadata
  getReport: async (reportId: string) => {
    const response = await apiClient.get(`/api/v1/report/${reportId}`);
    return response.data;
  },

  // List reports for audit
  listReports: async (auditId: string) => {
    const response = await apiClient.get(`/api/v1/audit/${auditId}/reports`);
    return response.data;
  },
};

export default api;
