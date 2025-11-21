# 🛡️ SentryAudit AI

**Enterprise-Grade Smart Contract Security Auditor**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)

SentryAudit AI is a production-ready, AI-powered smart contract security auditing platform that combines static analysis, machine learning, and expert security rules to identify vulnerabilities in Solidity, Vyper, and Move smart contracts.

---

## 🌟 Features

### Core Capabilities
- ✅ **20+ Vulnerability Detectors** - Comprehensive security analysis covering critical vulnerabilities
- 🤖 **AI-Powered Analysis** - Claude AI integration for deep reasoning and logic flaw detection
- 📊 **Gas Optimization** - Identifies gas-inefficient patterns and provides optimization recommendations
- 📄 **Professional Reports** - Export audit results in PDF, JSON, HTML, and Markdown formats
- 🎨 **Beautiful UI** - Stunning deep-red themed interface with real-time analysis (coming soon)
- 🔍 **Multi-Language Support** - Solidity, Vyper, and Move (Aptos/Sui)
- 🚀 **Production-Ready** - Fully containerized with Docker, horizontally scalable

### Vulnerability Detection
- **Critical:** Reentrancy, Access Control Bypass, Delegatecall to Untrusted Contracts
- **High:** tx.origin Authentication, Unchecked External Calls, Integer Overflow/Underflow
- **Medium:** Unbounded Loops, Floating Pragma, Deprecated Functions
- **Low:** Missing Events, Inefficient Storage, Naming Conventions
- **Gas Optimizations:** Storage in loops, poor packing, public vs external, and more

### AI Analysis
- Architectural security review
- Logic flaw detection
- Economic security analysis (DeFi-specific)
- Best practice violations
- Code quality assessment
- Fix recommendations with code examples

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Anthropic API key (for AI analysis)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/EmekaIwuagwu/sentry-audit.git
cd sentry-audit
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

### Quick Test

Try auditing the sample vulnerable contract:

```bash
curl -X POST http://localhost:8000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "$(cat examples/vulnerable_contract_1.sol)",
    "language": "solidity",
    "compiler_version": "0.7.6"
  }'
```

---

## 📖 API Usage

### Create Audit
```bash
POST /api/v1/audit
Content-Type: application/json

{
  "code": "contract MyContract { ... }",
  "language": "solidity",
  "compiler_version": "0.8.20",
  "optimization_enabled": true
}
```

### Get Audit Results
```bash
GET /api/v1/audit/{audit_id}
```

### Generate Report
```bash
POST /api/v1/report/generate
Content-Type: application/json

{
  "audit_id": "your-audit-id",
  "format": "pdf"
}
```

### Download Report
```bash
GET /api/v1/report/{report_id}/download
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend UI   │ ← React + TypeScript + Tailwind CSS (Coming Soon)
└────────┬────────┘
         │
    ┌────▼─────┐
    │   API    │ ← FastAPI REST API
    │  Gateway │
    └────┬─────┘
         │
    ┌────▼─────────────────────────┐
    │   Audit Processing Engine    │
    ├──────────────────────────────┤
    │ • AST Parser                 │
    │ • Static Analyzer (Slither)  │
    │ • AI Reasoning Engine (LLM)  │
    │ • Security Rule Engine       │
    │ • Gas Optimizer              │
    │ • Report Generator           │
    └────┬─────────────────────────┘
         │
    ┌────▼─────┐
    │ Database │ ← PostgreSQL
    └──────────┘
```

### Technology Stack

**Backend**
- Python 3.11+ with FastAPI
- PostgreSQL 15 (Database)
- Redis (Caching & Task Queue)
- SQLAlchemy (ORM)
- Anthropic Claude API (AI Analysis)
- Slither (Static Analysis)
- WeasyPrint (PDF Generation)

**DevOps**
- Docker & Docker Compose
- Nginx (Reverse Proxy)
- GitHub Actions (CI/CD)

---

## 🛠️ Development

### Local Development Setup

1. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start PostgreSQL and Redis**
```bash
docker-compose up -d db redis
```

3. **Start the API server**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Run tests**
```bash
pytest --cov=app tests/
```

### Project Structure

```
sentry-audit/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core utilities (DB, cache)
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── analyzers/   # Static analysis
│   │   │   ├── detectors/   # Vulnerability detectors
│   │   │   └── ai/          # AI reasoning engine
│   │   ├── utils/            # Utilities
│   │   └── main.py           # FastAPI app
│   ├── tests/                # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── examples/                 # Sample contracts
├── docker-compose.yml
└── README.md
```

---

## 🧪 Sample Vulnerable Contracts

Located in `examples/`:
- `vulnerable_contract_1.sol` - Classic vulnerabilities (reentrancy, access control, tx.origin, etc.)
- `vulnerable_contract_2.sol` - DeFi-specific issues (unprotected init, mint, delegatecall, etc.)

---

## 📊 Vulnerability Detection

### Scoring System
- **Risk Score**: 0-100 (100 = safest)
- **Security Rating**: A+ to F
- **Weighted by Severity**:
  - Critical: 25 points each
  - High: 15 points each
  - Medium: 8 points each
  - Low: 3 points each
  - Info: 1 point each

---

## 📄 Report Formats

- **PDF**: Professional multi-page report with executive summary
- **JSON**: Machine-readable format for CI/CD integration
- **HTML**: Interactive web-based report with color-coded severity
- **Markdown**: Plain-text format for GitHub/GitLab

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sentryaudit

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
ANTHROPIC_API_KEY=your-key-here
AI_MODEL=claude-3-sonnet-20240229
AI_MAX_TOKENS=4096

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

---

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 💰 Grant Support

SentryAudit AI is seeking ecosystem grants to:
- Expand language support (Rust, Cairo, Yul)
- Build educational resources
- Host community security workshops
- Integrate with major development frameworks
- Provide free audits for open-source projects

**Impact Goals:**
- 10,000+ audits in first year
- 50,000+ vulnerabilities detected
- $100M+ in potential losses prevented
- 5,000+ active users

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenZeppelin** - Security best practices and SafeMath library
- **Trail of Bits** - Slither static analyzer
- **Anthropic** - Claude AI for deep reasoning
- **Ethereum Foundation** - Solidity compiler and standards
- **Smart Contract Security Community** - SWC registry and CWE mappings

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/EmekaIwuagwu/sentry-audit/issues)
- **Discussions:** [GitHub Discussions](https://github.com/EmekaIwuagwu/sentry-audit/discussions)

---

## ⚠️ Disclaimer

SentryAudit AI is an automated security analysis tool that helps identify common vulnerabilities in smart contracts. However, it should **not** be used as a substitute for professional security audits. Always have your production contracts reviewed by experienced security auditors before deployment.

---

<div align="center">
  <strong>Built with ❤️ for the Blockchain Security Community</strong>
  <br>
  <sub>Making smart contracts safer, one audit at a time.</sub>
</div>
