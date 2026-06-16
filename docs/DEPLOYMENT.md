# 🚢 Deployment Guide

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vercel        │────▶│   Railway        │────▶│   Supabase      │
│  (Next.js 15)   │     │  (FastAPI)       │     │ (PostgreSQL)    │
│  Frontend       │     │  Backend + ARQ   │     │ Auth + DB + RT  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
                        ┌───────┴───────┐
                        │   Redis       │
                        │  (Upstash)    │
                        │  Task Queue   │
                        └───────────────┘
```

---

## Prerequisites

1. **GitHub Account** — for repository hosting
2. **Vercel Account** — frontend deployment (free tier works)
3. **Railway Account** — backend deployment (or Render, Fly.io)
4. **Supabase Account** — database + auth
5. **Upstash Account** — Redis for ARQ task queue (free tier works)
6. **OpenAI Account** — API key for AI agents
7. **CoinGecko Account** — API key (free tier for basic usage)

---

## Step 1: Supabase Setup

### 1.1 Create Project
1. Go to [supabase.com](https://supabase.com) → New Project
2. Choose organization, name: `crypto-intelligence-ai`
3. Set a strong database password (save it!)
4. Choose region closest to your users
5. Wait for project creation (~2 minutes)

### 1.2 Run Schema Migration
1. In Supabase Dashboard → SQL Editor → New Query
2. Copy the ENTIRE contents of `database/schema.sql`
3. Paste and click "Run"
4. Verify: Go to Table Editor → you should see all 15 tables

### 1.3 Configure Authentication
1. Go to Authentication → Settings
2. Under "Site URL": `https://your-domain.vercel.app` (or `http://localhost:3000` for dev)
3. Under "Redirect URLs": Add `https://your-domain.vercel.app/**`
4. Enable Email/Password provider
5. Optionally enable Google OAuth:
   - Google Cloud Console → Create OAuth 2.0 Client
   - Add credentials to Supabase

### 1.4 Get API Keys
1. Go to Settings → API
2. Copy these values:
   - `Project URL` → `SUPABASE_URL`
   - `anon public key` → `SUPABASE_ANON_KEY` (for frontend)
   - `service_role key` → `SUPABASE_SERVICE_ROLE_KEY` (for backend only!)
   - `JWT Secret` → `SUPABASE_JWT_SECRET`

---

## Step 2: Upstash Redis Setup

### 2.1 Create Redis Instance
1. Go to [upstash.com](https://upstash.com) → Redis → Create Database
2. Choose region (same as your backend)
3. Note the `REDIS_URL` (starts with `rediss://`)

---

## Step 3: Backend Deployment (Railway)

### 3.1 Prepare Repository
Ensure your backend has these files:
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/pyproject.toml`

### 3.2 Deploy on Railway
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select your repository
3. Set root directory to `backend`
4. Add environment variables in Railway Dashboard:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # service_role key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database (Supabase Postgres connection)
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Redis (Upstash)
REDIS_URL=rediss://default:[TOKEN]@[HOST].upstash.io:6379

# OpenAI
OPENAI_API_KEY=sk-...

# CoinGecko
COINGECKO_API_URL=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=CG-...

# App Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.vercel.app
SECRET_KEY=generate-a-random-secret-key-here
```

5. Deploy!

### 3.3 Verify Backend
```bash
curl https://your-backend.railway.app/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

---

## Step 4: Frontend Deployment (Vercel)

### 4.1 Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Framework: Next.js (auto-detected)
5. Add environment variables:

```env
# Supabase (public keys only!)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...  # anon key (NOT service_role!)

# Backend API
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Site URL
NEXT_PUBLIC_SITE_URL=https://your-domain.vercel.app
```

6. Deploy!

### 4.2 Verify Frontend
1. Visit your Vercel URL
2. You should see the landing page
3. Try registering an account
4. Log in → you should see the dashboard

---

## Step 5: DNS & Custom Domain (Optional)

### 5.1 Add Custom Domain to Vercel
1. Vercel Dashboard → Settings → Domains
2. Add your domain (e.g., `cryptointel.ai`)
3. Follow DNS configuration instructions

### 5.2 Update Supabase Redirect URLs
1. Supabase → Authentication → Settings
2. Add `https://your-custom-domain.com/**` to redirect URLs

### 5.3 Update CORS in Backend
1. Railway Dashboard → Environment Variables
2. Update `CORS_ORIGINS` to include your custom domain

---

## Step 6: CI/CD (Optional)

### GitHub Actions for Backend

```yaml
# .github/workflows/backend.yml
name: Backend CI/CD
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -m pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        uses: railwayapp/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

### GitHub Actions for Frontend

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD
on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run type-check
      - run: cd frontend && npm run lint
```

---

## Environment Variable Checklist

| Variable | Where | Description |
|----------|-------|-------------|
| `SUPABASE_URL` | Backend + Frontend | Supabase project URL |
| `SUPABASE_ANON_KEY` | Frontend only | Supabase anonymous key (public) |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend only | Supabase service role (SECRET) |
| `SUPABASE_JWT_SECRET` | Backend only | JWT signing secret |
| `DATABASE_URL` | Backend only | PostgreSQL connection string |
| `REDIS_URL` | Backend only | Redis connection string |
| `OPENAI_API_KEY` | Backend only | OpenAI API key |
| `COINGECKO_API_KEY` | Backend only | CoinGecko API key |
| `NEXT_PUBLIC_API_URL` | Frontend only | Backend API base URL |
| `NEXT_PUBLIC_SITE_URL` | Frontend only | Frontend site URL |
| `CORS_ORIGINS` | Backend only | Comma-separated allowed origins |
| `SECRET_KEY` | Backend only | Random secret for session signing |

---

## Troubleshooting

### Backend won't start
- Check Railway logs for errors
- Verify Supabase connection string format: `postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
- For Supabase, use port `5432` (transaction pool) or `6543` (session pool)
- Verify all environment variables are set

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend (must include frontend URL)
- Check browser console for CORS errors

### Authentication not working
- Verify Supabase redirect URLs include your frontend domain
- Check that `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are correct
- Ensure `Site URL` in Supabase Auth settings matches

### Database schema issues
- Run the migration in Supabase SQL Editor manually
- Check for any error messages in the SQL output
- All tables must be created before the backend starts
