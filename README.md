# 🚀 Crypto Intelligence AI

> Advanced AI-powered cryptocurrency market analysis platform combining technical analysis, market sentiment, economic events, news intelligence, AI forecasting, and risk analysis.

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue)](https://typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Latest-green)](https://supabase.com/)

---

## 📊 Overview

Crypto Intelligence AI is a production-grade platform that empowers traders and investors with AI-driven market insights. Unlike trading bots, this platform focuses on **analysis and intelligence** — giving you the information you need to make informed decisions.

### ✨ Key Features

- **📈 Technical Analysis** — RSI, MACD, EMA, SMA, Bollinger Bands, support/resistance, pattern detection
- **📰 News Intelligence** — Real-time news aggregation with AI-powered sentiment classification
- **🌐 Market Sentiment** — Social media and news sentiment analysis with Fear & Greed Index
- **🏛️ Macro Economic Analysis** — Fed policy, CPI, interest rates, regulations impact analysis
- **🤖 AI Forecasting** — 24h, 3d, 7d, and 30d price forecasts with confidence scores
- **⚠️ Risk Analysis** — Volatility, VaR, Sharpe ratio, max drawdown, correlation matrix
- **💼 Portfolio Monitoring** — Track holdings, P&L, allocation, and risk exposure in real-time

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 15 Frontend (Vercel)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ Dashboard │  │ Watchlist│  │Portfolio │  │ Coin Detail │ │
│  └─────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │
│        │              │              │               │        │
│  ┌─────┴──────────────┴──────────────┴───────────────┴──────┐ │
│  │              React Query + Zustand + Supabase Client     │ │
│  └──────────────────────────┬──────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────┘
                              │ HTTP + WebSocket
┌─────────────────────────────┼────────────────────────────────┐
│                    FastAPI Backend (Railway)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │Coins API │  │Market API│  │Analysis  │  │ Portfolio   │ │
│  └─────┬─────┘  └────┬─────┘  │   API    │  │    API      │ │
│        │              │        └────┬─────┘  └──────┬──────┘ │
│  ┌─────┴──────────────┴──────────────┴───────────────┴──────┐ │
│  │                    7 AI Agents (OpenAI GPT-4o)            │ │
│  │  Technical | News | Sentiment | Macro | Forecast | Risk  │ │
│  │                    + Final Report Agent                    │ │
│  └──────────────────────────┬──────────────────────────────┘ │
│  ┌──────────────────────────┴──────────────────────────────┐ │
│  │         ARQ Workers (Price, News, Analysis, Forecast)    │ │
│  └──────────────────────────┬──────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────┘
                              │
┌─────────────────────────────┼────────────────────────────────┐
│                  Supabase PostgreSQL                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Coins   │  │ Prices   │  │News/Sent │  │Portfolio/WL │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
│                    + RLS + Realtime (WAL)                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 20
- **Python** >= 3.12
- **Docker** & Docker Compose
- **Supabase** account (free tier works)
- **OpenAI** API key
- **CoinGecko** API key (free tier available)

### 1. Clone & Environment

```bash
# Clone repository
git clone <repo-url> crypto-intelligence-ai
cd crypto-intelligence-ai

# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend environment
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your Supabase URL/keys
```

### 2. Database Setup (Supabase)

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor → run the schema migration:
   - Copy contents of `database/schema.sql`
   - Execute in Supabase SQL Editor
3. Enable Row Level Security on all tables (included in schema.sql)
4. Copy your project URL and keys to both `.env` files

### 3. Backend Setup

```bash
cd backend

# With Docker (recommended)
docker compose up -d

# Or manually
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** to see the application.

---

## 📁 Project Structure

```
crypto-intelligence-ai/
├── frontend/                    # Next.js 15 Application
│   ├── src/
│   │   ├── app/                 # App Router pages & layouts
│   │   │   ├── (auth)/          # Login, Register, Forgot Password
│   │   │   ├── (dashboard)/     # Protected dashboard pages
│   │   │   └── api/             # API routes (webhooks only)
│   │   ├── components/          # React components
│   │   │   ├── ui/              # ShadCN UI primitives
│   │   │   ├── layout/          # Navbar, Sidebar, Footer
│   │   │   ├── landing/         # Landing page sections
│   │   │   ├── dashboard/       # Dashboard widgets
│   │   │   ├── watchlist/       # Watchlist components
│   │   │   ├── coins/           # Coin detail components
│   │   │   ├── charts/          # Chart components
│   │   │   ├── portfolio/       # Portfolio components
│   │   │   └── shared/          # Shared components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities & API clients
│   │   │   ├── supabase/        # Supabase client configs
│   │   │   ├── api/             # FastAPI HTTP client
│   │   │   ├── utils/           # Formatters, constants
│   │   │   └── types/           # TypeScript interfaces
│   │   ├── store/               # Zustand stores
│   │   └── providers/           # React context providers
│   ├── middleware.ts            # Auth middleware
│   └── package.json
│
├── backend/                     # FastAPI Application
│   ├── app/
│   │   ├── main.py              # App factory
│   │   ├── core/                # Config, security, deps
│   │   ├── api/v1/              # REST API endpoints
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── agents/              # AI agents (7 total)
│   │   ├── analysis/            # Technical analysis
│   │   ├── integrations/        # External API clients
│   │   └── workers/             # ARQ background jobs
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   └── docker-compose.yml
│
├── database/                    # Database
│   └── schema.sql               # Complete PostgreSQL schema
│
└── docs/                        # Documentation
    ├── DEPLOYMENT.md
    └── API.md
```

---

## 🎨 Design System

| Token | Light | Dark |
|-------|-------|------|
| Primary BG | `#FFFFFF` | `#0F172A` |
| Secondary BG | `#F8FAFC` | `#1E293B` |
| Card BG | `#FFFFFF` | `#1E293B` |
| Primary Text | `#0F172A` | `#F8FAFC` |
| Secondary Text | `#64748B` | `#94A3B8` |
| Accent | Gradient Blue | Gradient Blue |
| Success | `#22C55E` | `#4ADE80` |
| Warning | `#F59E0B` | `#FBBF24` |
| Danger | `#EF4444` | `#F87171` |

---

## 🤖 AI Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| Technical Analyst | RSI, MACD, EMA, Bollinger, patterns, S/R levels | GPT-4o |
| News Analyst | Classify news bullish/bearish/neutral | GPT-4o |
| Sentiment Analyst | Aggregate social + news sentiment | GPT-4o |
| Macro Analyst | Fed, CPI, rates, regulations impact | GPT-4o |
| Forecast Agent | Prophet + GPT forecast interpretation | GPT-4o |
| Risk Analyst | Volatility, VaR, Sharpe, drawdown | GPT-4o |
| Final Report | Executive summary + overall rating | GPT-4o |

---

## 📡 API Endpoints

See [docs/API.md](docs/API.md) for complete API documentation.

| Group | Endpoints |
|-------|-----------|
| Auth | `GET /api/v1/auth/verify` |
| Users | `GET\|PATCH /api/v1/users/me`, `/users/preferences` |
| Market | `GET /api/v1/market/overview`, `/trending`, `/top-movers`, `/search` |
| Coins | `GET /api/v1/coins`, `/coins/{id}`, `/coins/{id}/prices` |
| Watchlist | Full CRUD at `/api/v1/watchlists` |
| Portfolio | CRUD at `/api/v1/portfolio` |
| Analysis | `POST /api/v1/analysis/{agent}/{coin_id}`, `/analysis/full/{coin_id}` |
| Forecasts | `GET\|POST /api/v1/forecasts/{coin_id}` |
| News | `GET /api/v1/news`, `/news/coin/{coin_id}`, `/news/sentiment` |

---

## 🔐 Security

- **Authentication**: Supabase Auth with Row Level Security
- **JWT Verification**: Tokens validated in both Next.js middleware and FastAPI backend
- **RLS Policies**: User data isolated at database level
- **Rate Limiting**: API rate limiting via slowapi
- **Input Validation**: Zod (frontend) + Pydantic (backend)

---

## 🚢 Deployment

### Frontend → Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Backend → Railway
```bash
railway up
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

Built with ❤️ using Next.js, FastAPI, Supabase, and OpenAI.
