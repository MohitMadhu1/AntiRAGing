<p align="center">
  <img src="frontend/public/favicon.ico" alt="AntiRAGing" width="100" />
</p>
<h1 align="center">AntiRAGing</h1>

<p align="center">
  <a href="https://antiraging.vercel.app/">
    <img src="https://img.shields.io/badge/LIVE_DEMO-antiraging.vercel.app-ff0055?style=for-the-badge&logo=vercel&logoColor=white" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-000?style=flat-square&logo=nextdotjs" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
</p>

---

Paste a GitHub URL → get a structured, queryable onboarding guide for any codebase in minutes. Complete with intelligent code chunking, vector embeddings, and LangGraph multi-agent analysis.

## How it works

1. You log in via **GitHub OAuth** and paste a repository URL.
2. A background **Celery worker** kicks off: cloning the repo, discovering files, and parsing them into intelligent chunks using Tree-Sitter.
3. Chunks are embedded and stored in **PostgreSQL (pgvector)** via Neon.
4. **LangGraph** agents analyze the codebase structure, entry points, and business logic to generate a comprehensive markdown guide.
5. You watch the entire process live via **Server-Sent Events (SSE)** in a beautiful "Paper & Ink" UI dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                    │
│              Vercel · antiraging.vercel.app              │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  CORE API (FastAPI)                     │
│                  Render · Docker                        │
│                                                         │
│  /api/auth/*      → GitHub OAuth login                  │
│  /api/jobs/*      → Submit ingestion & SSE progress     │
│  /api/guides/*    → Fetch generated guides              │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │ SSE Stream   │  │ Celery Queue │  │ LangGraph AI  │  │
│  │ real-time    │  │ workers      │  │ agents        │  │
│  └─────────────┘  └──────┬───────┘  └───────┬───────┘   │
└──────────────────────────┼──────────────────┼───────────┘
                           │                  │
       ▼───────────────────▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────────┐
│  PostgreSQL  │  │    Redis     │  │  LLM Service    │
│  Neon        │  │  Upstash     │  │  Gemini / Groq  │
│  (pgvector)  │  │              │  │                 │
│              │  │  celery queue│  │  Analyzes code  │
│  users       │  │  SSE pub/sub │  │  Generates docs │
│  jobs/guides │  │  progress    │  │                 │
│  embeddings  │  │              │  │                 │
└──────────────┘  └──────────────┘  └─────────────────┘
```

## Features

| Feature | Description |
|---|---|
| **Intelligent Chunking** | Uses Tree-Sitter to semantically parse code (Python, JS, TS, Go, Java), keeping functions and classes intact for better context. |
| **Multi-Agent Analysis** | LangGraph coordinates specialized agents to analyze repository structure, document core logic, and write onboarding guides. |
| **Real-time SSE Tracking** | The frontend uses Server-Sent Events to stream exactly what the backend workers are doing in real-time. |
| **GitHub OAuth** | Secure login using GitHub to authorize repository access. |
| **Paper & Ink UI** | A completely custom, responsive, "sketchy" design system with built-in Light/Dark mode toggling. |
| **Vector Search Ready** | Code chunks are embedded into PostgreSQL via `pgvector`, making the codebase instantly queryable for RAG. |

## Run locally

Prerequisites: **Node 20+**, **Python 3.12+**, **Docker (Optional)**

```bash
# 1. Clone and configure
git clone https://github.com/MohitMadhu1/AntiRAGing.git
cd AntiRAGing
cp .env.example .env
# Fill in DATABASE_URL (Neon), REDIS_URL (Upstash), GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GEMINI_API_KEY

# 2. Start Backend & Celery
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
./start.sh  # Runs FastAPI and Celery worker simultaneously

# 3. Start Frontend
cd ../frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Deployment

This runs on a highly efficient serverless/containerized stack:

| Service | Platform |
|---|---|
| Frontend | [Vercel](https://vercel.com) |
| FastAPI & Celery | [Render](https://render.com) (Docker) |
| PostgreSQL + pgvector | [Neon](https://neon.tech) |
| Redis | [Upstash](https://upstash.com) |

## Project structure

```
AntiRAGing/
├── backend/                 # FastAPI + Celery
│   ├── app/
│   │   ├── api/             # REST endpoints (auth, jobs, guides)
│   │   ├── chunking/        # Tree-sitter semantic chunking logic
│   │   ├── workers/         # Celery tasks (ingestion, LangGraph triggers)
│   │   ├── agents/          # LangGraph state machines and AI logic
│   │   └── services/        # Postgres/pgvector and Embedding services
│   ├── start.sh             # Unified startup script
│   └── Dockerfile
├── frontend/                # Next.js App Router
│   ├── src/app/
│   │   ├── dashboard/       # Repository list and job submission
│   │   ├── jobs/[id]/       # Live SSE progress tracking
│   │   └── guide/[id]/      # Rendered markdown onboarding guide
│   ├── src/components/      # Custom Sketch UI components
│   └── globals.css          # Paper & Ink / Dark Mode CSS
└── .env.example
```
