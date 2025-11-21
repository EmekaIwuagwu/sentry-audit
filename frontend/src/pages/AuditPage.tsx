import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Editor from '@monaco-editor/react';
import { Play, Upload, Settings } from 'lucide-react';
import { useAuditStore } from '@/store/auditStore';
import { api } from '@/services/api';
import type { ContractLanguage } from '@/types';

const SAMPLE_CONTRACT = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleBank {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // Vulnerable: External call before state change
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] -= amount;
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}`;

export const AuditPage = () => {
  const navigate = useNavigate();
  const {
    currentCode,
    setCode,
    language,
    setLanguage,
    compilerVersion,
    setCompilerVersion,
    optimizationEnabled,
    setOptimizationEnabled,
    setIsLoading,
    setError,
    setCurrentAuditId,
  } = useAuditStore();

  const [code, setLocalCode] = useState(currentCode || SAMPLE_CONTRACT);

  const handleAudit = async () => {
    if (!code.trim()) {
      setError('Please enter contract code');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setCode(code);

      const response = await api.createAudit({
        code,
        language,
        compiler_version: compilerVersion,
        optimization_enabled: optimizationEnabled,
      });

      setCurrentAuditId(response.audit_id);

      // Poll for results
      const poll = async () => {
        const result = await api.getAudit(response.audit_id);
        if (result.status === 'completed' || result.status === 'failed') {
          setIsLoading(false);
          navigate(`/results/${response.audit_id}`);
        } else {
          setTimeout(poll, 2000);
        }
      };

      poll();
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message || 'Audit failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Smart Contract Auditor</h1>
          <p className="text-text-secondary">
            Paste your smart contract code below and click "Run Audit" to start the analysis
          </p>
        </div>

        {/* Controls */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as ContractLanguage)}
                className="w-full bg-background-elevated border border-border-subtle rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
              >
                <option value="solidity">Solidity</option>
                <option value="vyper">Vyper</option>
                <option value="move">Move</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Compiler Version</label>
              <input
                type="text"
                value={compilerVersion}
                onChange={(e) => setCompilerVersion(e.target.value)}
                className="w-full bg-background-elevated border border-border-subtle rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                placeholder="0.8.20"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Optimization</label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={optimizationEnabled}
                  onChange={(e) => setOptimizationEnabled(e.target.checked)}
                  className="w-5 h-5 rounded text-primary-600 focus:ring-primary-500"
                />
                <span>Enabled</span>
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleAudit}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Play size={18} />
                Run Audit
              </button>
            </div>
          </div>
        </div>

        {/* Editor */}
        <div className="card p-0 overflow-hidden">
          <div className="bg-background-elevated px-4 py-2 border-b border-border-subtle flex items-center justify-between">
            <span className="text-sm font-medium">Contract Code</span>
            <button className="text-text-secondary hover:text-white flex items-center gap-2 text-sm">
              <Upload size={16} />
              Upload File
            </button>
          </div>
          <Editor
            height="600px"
            defaultLanguage="solidity"
            value={code}
            onChange={(value) => setLocalCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>
      </motion.div>
    </div>
  );
};
