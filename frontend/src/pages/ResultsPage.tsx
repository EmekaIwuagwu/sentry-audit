import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { AlertTriangle, Download, TrendingUp, Shield } from 'lucide-react';
import { api } from '@/services/api';
import type { VulnerabilitySeverity } from '@/types';

const severityColors: Record<VulnerabilitySeverity, string> = {
  critical: 'text-severity-critical bg-severity-critical/10 border-severity-critical',
  high: 'text-severity-high bg-severity-high/10 border-severity-high',
  medium: 'text-severity-medium bg-severity-medium/10 border-severity-medium',
  low: 'text-severity-low bg-severity-low/10 border-severity-low',
  info: 'text-severity-info bg-severity-info/10 border-severity-info',
};

export const ResultsPage = () => {
  const { auditId } = useParams<{ auditId: string }>();

  const { data: audit, isLoading, error } = useQuery({
    queryKey: ['audit', auditId],
    queryFn: () => api.getAudit(auditId!),
    enabled: !!auditId,
    refetchInterval: (data) =>
      data?.status === 'processing' || data?.status === 'pending' ? 2000 : false,
  });

  const handleDownloadReport = async (format: 'pdf' | 'json' | 'html' | 'markdown') => {
    if (!auditId) return;
    try {
      const report = await api.generateReport({ audit_id: auditId, format });
      const blob = await api.downloadReport(report.report_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = report.file_name;
      a.click();
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  if (isLoading || !audit) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500 mx-auto mb-4"></div>
        <p className="text-text-secondary">Analyzing contract...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <AlertTriangle className="text-severity-high mx-auto mb-4" size={48} />
        <p className="text-text-secondary">Failed to load audit results</p>
      </div>
    );
  }

  const totalVulns =
    audit.vulnerability_counts.critical +
    audit.vulnerability_counts.high +
    audit.vulnerability_counts.medium +
    audit.vulnerability_counts.low +
    audit.vulnerability_counts.info;

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Audit Results</h1>
            <p className="text-text-secondary">Audit ID: {audit.audit_id}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleDownloadReport('pdf')}
              className="btn-primary flex items-center gap-2"
            >
              <Download size={18} />
              Download PDF
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card text-center">
            <div className="text-5xl font-bold mb-2 text-primary-500">
              {audit.security_rating || 'N/A'}
            </div>
            <div className="text-text-secondary">Security Rating</div>
          </div>

          <div className="card text-center">
            <div className="text-5xl font-bold mb-2 text-primary-500">{audit.risk_score}</div>
            <div className="text-text-secondary">Risk Score (0-100)</div>
          </div>

          <div className="card text-center">
            <div className="text-5xl font-bold mb-2 text-severity-critical">
              {audit.vulnerability_counts.critical}
            </div>
            <div className="text-text-secondary">Critical Issues</div>
          </div>

          <div className="card text-center">
            <div className="text-5xl font-bold mb-2">{totalVulns}</div>
            <div className="text-text-secondary">Total Issues</div>
          </div>
        </div>

        {/* Vulnerability Counts */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Vulnerability Breakdown</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(audit.vulnerability_counts).map(([severity, count]) => (
              <div key={severity} className="text-center p-4 rounded-lg border border-border-subtle">
                <div className={`text-3xl font-bold mb-1 text-severity-${severity}`}>{count}</div>
                <div className="text-sm text-text-secondary capitalize">{severity}</div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Summary */}
        {audit.ai_analysis?.summary && (
          <div className="card mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Shield size={24} />
              AI Analysis Summary
            </h2>
            <p className="text-text-secondary leading-relaxed">{audit.ai_analysis.summary}</p>
          </div>
        )}

        {/* Vulnerabilities */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">
            Vulnerabilities Found ({audit.vulnerabilities.length})
          </h2>

          {audit.vulnerabilities.length === 0 ? (
            <div className="card text-center py-12">
              <Shield className="text-primary-500 mx-auto mb-4" size={48} />
              <p className="text-xl font-semibold mb-2">No vulnerabilities found!</p>
              <p className="text-text-secondary">Your contract looks secure.</p>
            </div>
          ) : (
            audit.vulnerabilities.map((vuln) => (
              <motion.div
                key={vuln.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`card border-l-4 ${severityColors[vuln.severity].split(' ')[2]}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-bold">{vuln.title}</h3>
                  <span className={`severity-badge severity-${vuln.severity}`}>
                    {vuln.severity}
                  </span>
                </div>

                <p className="text-text-secondary mb-4">{vuln.description}</p>

                {vuln.location.line && (
                  <p className="text-sm text-text-muted mb-2">
                    Location: Line {vuln.location.line}
                    {vuln.location.function && ` in function ${vuln.location.function}()`}
                  </p>
                )}

                {vuln.code_snippet && (
                  <pre className="bg-background-dark p-4 rounded-lg overflow-x-auto text-sm mb-4">
                    <code>{vuln.code_snippet}</code>
                  </pre>
                )}

                {vuln.recommendation && (
                  <div className="bg-primary-900/20 border border-primary-700 rounded-lg p-4">
                    <p className="font-semibold mb-2 text-primary-400">💡 Recommendation:</p>
                    <p className="text-sm text-text-secondary">{vuln.recommendation}</p>
                  </div>
                )}
              </motion.div>
            ))
          )}
        </div>

        {/* Gas Optimizations */}
        {audit.gas_analysis?.optimizations && audit.gas_analysis.optimizations.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <TrendingUp size={24} />
              Gas Optimization Opportunities
            </h2>
            <div className="space-y-4">
              {audit.gas_analysis.optimizations.map((opt, index) => (
                <div key={index} className="card border-l-4 border-severity-info">
                  <h3 className="font-bold mb-2">{opt.issue}</h3>
                  <p className="text-sm text-text-secondary mb-2">
                    Potential savings: {opt.savings || 'Variable'}
                  </p>
                  <p className="text-sm text-text-muted">{opt.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};
