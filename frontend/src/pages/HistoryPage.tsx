import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { api } from '@/services/api';
import type { AuditStatus } from '@/types';

const statusIcons: Record<AuditStatus, React.ReactNode> = {
  completed: <CheckCircle className="text-green-500" />,
  failed: <AlertTriangle className="text-red-500" />,
  processing: <Clock className="text-yellow-500 animate-spin" />,
  pending: <Clock className="text-gray-500" />,
};

export const HistoryPage = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['audits'],
    queryFn: () => api.listAudits(),
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-6xl mx-auto"
      >
        <h1 className="text-4xl font-bold mb-8">Audit History</h1>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500 mx-auto"></div>
          </div>
        ) : data?.audits?.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-xl text-text-secondary mb-4">No audits yet</p>
            <Link to="/audit" className="btn-primary inline-block">
              Start Your First Audit
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {data?.audits?.map((audit: any) => (
              <Link
                key={audit.id}
                to={`/results/${audit.id}`}
                className="card hover:shadow-glow transition-all block"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div>{statusIcons[audit.status as AuditStatus]}</div>
                    <div>
                      <div className="font-semibold">{audit.language} Contract</div>
                      <div className="text-sm text-text-secondary">
                        {new Date(audit.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-500">
                      {audit.security_rating || '-'}
                    </div>
                    <div className="text-sm text-text-secondary">Rating</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};
