import { Link } from 'react-router-dom';
import { ShieldLogo } from '@/components/common/ShieldLogo';
import { Shield, Zap, FileText, Brain, TrendingUp, Lock } from 'lucide-react';
import { motion } from 'framer-motion';

export const HomePage = () => {
  const features = [
    {
      icon: Shield,
      title: '20+ Vulnerability Detectors',
      description: 'Comprehensive analysis covering critical to info severity levels',
    },
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Claude AI integration for deep reasoning and logic flaw detection',
    },
    {
      icon: TrendingUp,
      title: 'Gas Optimization',
      description: 'Identifies inefficient patterns and provides optimization recommendations',
    },
    {
      icon: FileText,
      title: 'Professional Reports',
      description: 'Export audit results in PDF, JSON, HTML, and Markdown formats',
    },
    {
      icon: Zap,
      title: 'Instant Results',
      description: 'Complete security analysis in under 60 seconds',
    },
    {
      icon: Lock,
      title: 'Production Ready',
      description: 'Enterprise-grade security auditing platform',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <div className="relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-900 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-primary-800 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Hero Section */}
      <section className="relative container mx-auto px-4 py-20 md:py-32">
        <motion.div
          className="text-center max-w-5xl mx-auto"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          {/* Logo */}
          <motion.div variants={itemVariants} className="flex justify-center mb-8">
            <ShieldLogo size={120} animate={true} />
          </motion.div>

          {/* Title */}
          <motion.h1
            variants={itemVariants}
            className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary-500 via-primary-600 to-primary-400 bg-clip-text text-transparent"
          >
            SentryAudit AI
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            variants={itemVariants}
            className="text-xl md:text-2xl text-text-secondary mb-4"
          >
            Enterprise-Grade Smart Contract Security Auditor
          </motion.p>

          <motion.p
            variants={itemVariants}
            className="text-lg text-text-muted mb-12 max-w-3xl mx-auto"
          >
            AI-powered security auditing platform combining static analysis, machine learning,
            and expert security rules to identify vulnerabilities in your smart contracts.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link
              to="/audit"
              className="btn-primary text-lg px-8 py-4 shadow-glow-strong hover:scale-105 transform transition-transform"
            >
              Start Free Audit
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-lg px-8 py-4"
            >
              View API Docs
            </a>
          </motion.div>

          {/* Stats */}
          <motion.div
            variants={itemVariants}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 max-w-4xl mx-auto"
          >
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary-500">20+</div>
              <div className="text-sm text-text-secondary mt-1">Vulnerability Types</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary-500">&lt;60s</div>
              <div className="text-sm text-text-secondary mt-1">Analysis Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary-500">100%</div>
              <div className="text-sm text-text-secondary mt-1">Free & Open Source</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary-500">4</div>
              <div className="text-sm text-text-secondary mt-1">Report Formats</div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative container mx-auto px-4 py-20">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
        >
          <motion.h2
            variants={itemVariants}
            className="text-3xl md:text-4xl font-bold text-center mb-16"
          >
            Powerful Features
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="card hover:shadow-glow transition-all duration-300 hover:scale-105"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-primary-900 rounded-lg">
                    <feature.icon className="text-primary-500" size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                    <p className="text-text-secondary text-sm">{feature.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section className="relative container mx-auto px-4 py-20">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="card-elevated text-center max-w-3xl mx-auto p-12"
        >
          <motion.h2
            variants={itemVariants}
            className="text-3xl font-bold mb-4"
          >
            Ready to Secure Your Smart Contracts?
          </motion.h2>
          <motion.p
            variants={itemVariants}
            className="text-text-secondary mb-8"
          >
            Start your free audit now. No registration required.
          </motion.p>
          <motion.div variants={itemVariants}>
            <Link
              to="/audit"
              className="btn-primary text-lg px-8 py-4 inline-block shadow-glow-strong hover:scale-105 transform transition-transform"
            >
              Launch Auditor
            </Link>
          </motion.div>
        </motion.div>
      </section>
    </div>
  );
};
