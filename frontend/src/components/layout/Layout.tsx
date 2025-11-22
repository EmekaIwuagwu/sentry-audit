import { Link, useLocation } from 'react-router-dom';
import { Shield, FileText, History } from 'lucide-react';
import { ShieldLogo } from '../common/ShieldLogo';
import { motion } from 'framer-motion';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-background-dark">
      {/* Navigation */}
      <nav className="bg-background-card border-b border-border-subtle">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand */}
            <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <ShieldLogo size={40} />
              <div>
                <h1 className="text-2xl font-bold text-primary-500">
                  SentryAudit <span className="text-white">AI</span>
                </h1>
                <p className="text-xs text-text-secondary">Smart Contract Security Auditor</p>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-6">
              <Link
                to="/audit"
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isActive('/audit')
                    ? 'bg-primary-700 text-white shadow-glow'
                    : 'text-text-secondary hover:text-white hover:bg-background-elevated'
                }`}
              >
                <FileText size={18} />
                <span className="font-medium">New Audit</span>
              </Link>

              <Link
                to="/history"
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isActive('/history')
                    ? 'bg-primary-700 text-white shadow-glow'
                    : 'text-text-secondary hover:text-white hover:bg-background-elevated'
                }`}
              >
                <History size={18} />
                <span className="font-medium">History</span>
              </Link>

              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-secondary hover:text-white px-4 py-2 rounded-lg hover:bg-background-elevated transition-all"
              >
                API Docs
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-80px)]">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-background-card border-t border-border-subtle py-8 mt-20">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Shield className="text-primary-500" size={20} />
              <span className="text-text-secondary text-sm">
                © 2025 SentryAudit AI. Making smart contracts safer.
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-text-secondary">
              <a
                href="https://github.com/EmekaIwuagwu/sentry-audit"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 transition-colors"
              >
                GitHub
              </a>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 transition-colors"
              >
                API Documentation
              </a>
              <span>v1.0.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
