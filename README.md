# 🚀 AI Workflow Automation Hub

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://langchain.com/)
[![n8n](https://img.shields.io/badge/n8n-latest-red.svg)](https://n8n.io/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Enterprise B2B automation platform combining **n8n** (visual workflow engine) with **LangChain + Google Gemini** (AI orchestration) to intelligently process leads, route emails, generate content, and analyze documents — fully containerized and production-ready.

---

## 🎯 Problem Solved

B2B companies receiving 500+ leads/day and 200+ emails/day face:

- ❌ Sales teams wasting time on unqualified leads
- ❌ Emails getting lost or mis-routed
- ❌ Content creation that is slow and expensive
- ❌ Manual processes that don't scale

**This platform delivers:**

- ✅ AI agents that qualify leads with rule-based fallback — always reliable
- ✅ Email routing that reduces manual triage by 80%
- ✅ AI content generation with human-in-the-loop review
- ✅ Visual n8n workflows + Python power = flexible and maintainable

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  React Dashboard  (Port 3000)                │
└────────────────────────┬─────────────────────────────────────┘
                         │ REST
┌────────────────────────▼─────────────────────────────────────┐
│              FastAPI Backend  (Port 8000)                    │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                  LangChain Layer                      │   │
│  │  Agents : LeadQualifier · EmailRouter · ContentCreator│   │
│  │  Chains : EmailAnalysis · DocumentProcessing          │   │
│  │  Tools  : CompanySize · IndustryFit · Urgency · Enrich│   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────┬────────────────────────┘
               │                      │
┌──────────────▼──────────┐  ┌────────▼──────────────────────┐
│   n8n Engine (5678)     │  │  Google Gemini API (Free)      │
│   4 Production Workflows│  └───────────────────────────────┘
│   Custom AI Nodes       │
└──────────────┬──────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│               PostgreSQL 16  (Port 5432)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🤖 LangChain AI Layer

- **3 ReAct Agents**: Lead Qualifier, Email Router, Content Creator
- **2 Sequential Chains**: Email Analysis (4-step), Document Processing (4-step)
- **5 Custom Tools**: `score_company_size`, `analyze_industry_fit`, `calculate_urgency_signals`, `enrich_company_data`, `extract_contact_info`
- **Robust fallbacks**: Rule-based scoring when LLM is unavailable

### 🔄 n8n Workflows (3 ready-to-import JSON files)

- **Lead Qualification**: Webhook → AI Score → Airtable routing + Slack alert
- **Email Intelligence**: IMAP poll → AI classify → Route to correct team
- **Content Pipeline**: Daily schedule → Generate → Notify team

### 📊 React Dashboard

- Real-time workflow status monitoring with live polling
- Analytics tabs: executions, success rate, token usage
- Skeleton loading states and error handling

### 🛠️ Developer Experience

- FastAPI with auto-generated Swagger docs at `/docs`
- Full Pydantic validation on all endpoints
- Pytest suite with 15+ tests and mocked LLM calls
- `make` commands for every workflow

---

## 📋 Prerequisites

- Docker 24.0+ and Docker Compose 2.0+
- Git
- **Google Gemini API key (FREE)** → https://makersuite.google.com/app/apikey
- 4 GB RAM, 10 GB disk

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/WaltGreenwich/ai-workflow-automation.git
cd ai-workflow-automation
```

### 2. Setup

```bash
make setup
```

Edit `.env` and add your `GOOGLE_API_KEY`.

### 3. Launch

```bash
make up
```

### 4. Verify

```bash
make health
```

### 5. Test the API

```bash
make demo
```

---

## 🌐 Service URLs

| Service                | URL                        | Credentials                 |
| ---------------------- | -------------------------- | --------------------------- |
| **Frontend Dashboard** | http://localhost:3000      | —                           |
| **Backend API**        | http://localhost:8000      | —                           |
| **Swagger Docs**       | http://localhost:8000/docs | —                           |
| **n8n Workflows**      | http://localhost:5678      | admin / admin123            |
| **PostgreSQL**         | localhost:5432             | workflowuser / workflowpass |

---

## 📥 Import n8n Workflows

```bash
make import-workflows
```

Follow the printed instructions to import the 3 JSON files from `./n8n/workflows/`.

---

## 🧪 Testing

```bash
make test          # Full suite + coverage report
make test-watch    # Watch mode
```

---

## 📡 API Reference

### `POST /api/v1/langchain/qualify-lead`

```json
{
  "name": "John Doe",
  "company": "TechCorp",
  "email": "john@techcorp.com",
  "industry": "Technology",
  "employees": 500,
  "message": "Need AI automation ASAP"
}
```

Response:

```json
{
  "score": 85,
  "category": "Enterprise",
  "reasoning": "Large tech company with urgency signals",
  "next_action": "immediate_contact",
  "suggested_message": "Hi John, I noticed TechCorp might benefit..."
}
```

Other endpoints:

- `POST /api/v1/langchain/analyze-email`
- `POST /api/v1/langchain/generate-content`
- `POST /api/v1/langchain/process-document`
- `POST /api/v1/langchain/classify`
- `GET  /api/v1/workflows`
- `GET  /api/v1/analytics/metrics`
- `GET  /api/v1/health`

Full interactive docs: http://localhost:8000/docs

---

## 🛠️ Make Commands

| Command                 | Description                 |
| ----------------------- | --------------------------- |
| `make setup`            | First-time setup            |
| `make up`               | Start all services          |
| `make down`             | Stop all services           |
| `make logs`             | Live logs                   |
| `make test`             | Tests + coverage            |
| `make health`           | Health check                |
| `make demo`             | Test qualify-lead API       |
| `make shell-backend`    | Shell into backend          |
| `make clean`            | Remove containers + volumes |
| `make rebuild`          | Full rebuild                |
| `make import-workflows` | n8n import instructions     |

---

## 📁 Project Structure

```
ai-workflow-automation/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Pydantic settings
│   │   ├── database.py                # SQLAlchemy async setup
│   │   ├── langchain_layer/           # ⭐ AI CORE
│   │   │   ├── agents/                # ReAct agents (3)
│   │   │   ├── chains/                # Sequential chains (2)
│   │   │   ├── tools/                 # @tool functions (5)
│   │   │   └── memory/                # Conversation memory
│   │   ├── api/routes/                # FastAPI endpoints
│   │   └── models/                    # SQLAlchemy + Pydantic
│   ├── tests/                         # Pytest (15+ tests)
│   ├── init.sql                       # DB schema + seed data
│   ├── requirements.txt
│   └── Dockerfile
├── n8n/workflows/                     # JSON workflow exports (3)
├── frontend/src/                      # React + Tailwind
│   ├── components/
│   │   ├── WorkflowMonitor.jsx
│   │   └── AnalyticsDashboard.jsx
│   └── pages/Dashboard.jsx
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

---

## 🔧 Troubleshooting

**Backend not starting:**

```bash
docker compose logs backend
# Check GOOGLE_API_KEY is set in .env
docker compose restart backend
```

**n8n not importing workflows:**

```bash
# Import via UI: n8n → Workflows → + New → ... → Import from File
# Files are in ./n8n/workflows/
```

**Tests failing in CI (no API key):**

```bash
# Tests mock all LLM calls — GOOGLE_API_KEY is not required for tests
export GOOGLE_API_KEY=dummy
make test
```

---

## 🗺️ Roadmap

- [ ] LangSmith integration for LLMOps observability
- [ ] Make.com support alongside n8n
- [ ] Azure OpenAI / OpenAI model support
- [ ] A/B testing for prompt templates
- [ ] Terraform deployment to AWS/GCP
- [ ] Multi-tenant support

---

## 📝 License

MIT — see [LICENSE](LICENSE)

---

## 👤 Author

**Walt Greenwich** · [GitHub](https://github.com/WaltGreenwich) · [LinkedIn](#)

---

⭐ _If this helped you land the job, please star the repo!_
