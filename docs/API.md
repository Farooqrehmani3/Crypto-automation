# 📡 API Documentation

Base URL: `https://your-backend.railway.app/api/v1`

---

## Authentication

All endpoints (except public ones) require a Supabase JWT token in the `Authorization` header:

```
Authorization: Bearer <supabase-jwt-token>
```

### Verify Token
```
GET /auth/verify
```
Returns the authenticated user's information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## Users

### Get Current User
```
GET /users/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "preferences": { ... }
  }
}
```

### Update Current User
```
PATCH /users/me
```

**Request:**
```json
{
  "display_name": "John Doe"
}
```

### Get User Preferences
```
GET /users/preferences
```

**Response:**
```json
{
  "success": true,
  "data": {
    "default_timeframe": "1d",
    "default_chart_type": "candlestick",
    "theme": "dark",
    "notifications_enabled": true,
    "ai_analysis_auto": false,
    "favorite_indicators": ["RSI", "MACD", "EMA"],
    "risk_tolerance": "moderate"
  }
}
```

### Update User Preferences
```
PATCH /users/preferences
```

**Request:**
```json
{
  "default_timeframe": "4h",
  "theme": "dark"
}
```

---

## Market Data

### Market Overview
```
GET /market/overview
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_market_cap": 2500000000000,
    "total_volume_24h": 125000000000,
    "btc_dominance": 52.5,
    "eth_dominance": 18.2,
    "fear_greed_index": 65,
    "fear_greed_label": "Greed",
    "active_cryptocurrencies": 12500,
    "market_cap_change_pct_24h": 2.35
  }
}
```

### Trending Coins
```
GET /market/trending?limit=10
```

### Top Movers
```
GET /market/top-movers?direction=gainers&limit=10
```

Parameters:
- `direction`: `gainers` or `losers`
- `limit`: 1-100 (default 10)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "coin_id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price": 67500.50,
      "price_change_pct_24h": 5.23,
      "sparkline_7d": [...]
    }
  ]
}
```

### Search Coins
```
GET /market/search?q=bit&limit=20
```

---

## Coins

### List Coins
```
GET /coins?page=1&per_page=50&sort_by=market_cap_rank
```

Parameters:
- `page`: Page number
- `per_page`: Items per page (max 250)
- `sort_by`: `market_cap_rank`, `name`, `price_change_pct_24h`
- `category`: Optional category filter

### Get Coin Detail
```
GET /coins/{coin_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "coin_id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "image_url": "https://...",
    "market_cap_rank": 1,
    "current_price": 67500.50,
    "market_cap": 1320000000000,
    "total_volume": 35000000000,
    "price_change_24h": 3350.25,
    "price_change_pct_24h": 5.23,
    "price_change_pct_7d": 8.15,
    "price_change_pct_30d": 12.40,
    "circulating_supply": 19500000,
    "total_supply": 19500000,
    "max_supply": 21000000,
    "ath": 69000,
    "ath_date": "2021-11-10T00:00:00Z",
    "atl": 67.81,
    "atl_date": "2013-07-06T00:00:00Z",
    "sparkline_7d": [...]
  }
}
```

### Get Coin Prices (OHLCV)
```
GET /coins/{coin_id}/prices?timeframe=1d&limit=100
```

Parameters:
- `timeframe`: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, `1w`
- `from`: Start timestamp (ISO 8601)
- `to`: End timestamp (ISO 8601)
- `limit`: Max candles to return (default 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "open": 42500.00,
      "high": 43200.00,
      "low": 42400.00,
      "close": 43100.00,
      "volume": 12500000000
    }
  ],
  "meta": {
    "timeframe": "1d",
    "count": 100
  }
}
```

### Get Coin Stats
```
GET /coins/{coin_id}/stats
```

---

## Watchlists

### List Watchlists
```
GET /watchlists
```

### Create Watchlist
```
POST /watchlists
```

**Request:**
```json
{
  "name": "My Favorites"
}
```

### Update Watchlist
```
PATCH /watchlists/{id}
```

**Request:**
```json
{
  "name": "New Name"
}
```

### Delete Watchlist
```
DELETE /watchlists/{id}
```

### Get Watchlist Items
```
GET /watchlists/{id}/items
```

### Add Coin to Watchlist
```
POST /watchlists/{id}/items
```

**Request:**
```json
{
  "coin_id": "bitcoin"
}
```

### Remove Coin from Watchlist
```
DELETE /watchlists/{id}/items/{coin_id}
```

### Toggle Favorite
```
PATCH /watchlists/{id}/items/{coin_id}
```

**Request:**
```json
{
  "is_favorite": true
}
```

---

## Portfolio

### Get Portfolio Summary
```
GET /portfolio
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_value_usd": 125000.50,
    "total_cost_basis_usd": 100000.00,
    "total_pnl_usd": 25000.50,
    "total_pnl_pct": 25.00,
    "asset_count": 5
  }
}
```

### Add Holding
```
POST /portfolio/assets
```

**Request:**
```json
{
  "coin_id": "bitcoin",
  "quantity": 0.5,
  "average_buy_price": 42000.00
}
```

### Update Holding
```
PATCH /portfolio/assets/{id}
```

**Request:**
```json
{
  "quantity": 1.0,
  "average_buy_price": 43000.00
}
```

### Delete Holding
```
DELETE /portfolio/assets/{id}
```

### Get Performance History
```
GET /portfolio/performance?period=1m
```

Parameters:
- `period`: `1w`, `1m`, `3m`, `1y`, `all`

### Get Allocation
```
GET /portfolio/allocation
```

### Record Transaction
```
POST /portfolio/transactions
```

**Request:**
```json
{
  "portfolio_asset_id": "uuid",
  "type": "buy",
  "quantity": 0.1,
  "price_per_unit": 67000.00,
  "fee": 10.00,
  "transaction_date": "2024-01-15T10:30:00Z",
  "notes": "Bought the dip"
}
```

### Get Transactions
```
GET /portfolio/transactions?asset_id=uuid&page=1&per_page=20
```

---

## AI Analysis

### Run Single Agent Analysis
```
POST /analysis/technical/{coin_id}
POST /analysis/sentiment/{coin_id}
POST /analysis/macro/{coin_id}
POST /analysis/news/{coin_id}
POST /analysis/forecast/{coin_id}
POST /analysis/risk/{coin_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "status": "completed",
    "agent_type": "technical",
    "prediction": { ... }
  }
}
```

### Run Full Analysis (All Agents)
```
POST /analysis/full/{coin_id}
```

This triggers all 7 agents in parallel and generates a final report.

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "status": "pending",
    "estimated_duration_seconds": 30
  }
}
```

### Check Analysis Status
```
GET /analysis/status/{analysis_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "status": "running",
    "completed_agents": ["technical", "sentiment"],
    "pending_agents": ["news", "macro", "forecast", "risk", "report"],
    "started_at": "2024-01-01T00:00:00Z"
  }
}
```

### Get Full Report
```
GET /analysis/report/{analysis_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "coin_id": "bitcoin",
    "status": "completed",
    "duration_ms": 28500,
    "agents": {
      "technical": {
        "signal": "bullish",
        "confidence": 0.85,
        "indicators": {
          "rsi": 58.5,
          "macd": "bullish_cross",
          "ema_trend": "up"
        },
        "patterns": ["bullish_engulfing"],
        "support_levels": [65000, 63000],
        "resistance_levels": [69000, 72000],
        "reasoning": "The RSI at 58.5 shows room for upward movement..."
      },
      "news": { ... },
      "sentiment": { ... },
      "macro": { ... },
      "forecast": {
        "24h": {
          "predicted_price": 68500,
          "direction": "up",
          "upper_bound": 69500,
          "lower_bound": 67500,
          "confidence": 0.72
        },
        "3d": { ... },
        "7d": { ... },
        "30d": { ... }
      },
      "risk": { ... },
      "report": {
        "overall_rating": "BUY",
        "rating_score": 7.5,
        "executive_summary": "Bitcoin shows strong bullish signals...",
        "key_catalysts": ["ETF inflows", "Halving approaching"],
        "key_risks": ["Regulatory uncertainty", "Macro headwinds"],
        "price_targets": {
          "bullish": 75000,
          "base": 69000,
          "bearish": 62000
        }
      }
    }
  }
}
```

### Get Analysis History
```
GET /analysis/history/{coin_id}?page=1&per_page=10
```

---

## Forecasts

### Get Latest Forecast
```
GET /forecasts/{coin_id}?horizon=7d
```

Parameters:
- `horizon`: `24h`, `3d`, `7d`, `30d`

**Response:**
```json
{
  "success": true,
  "data": {
    "horizon": "7d",
    "predicted_price": 69500,
    "predicted_direction": "up",
    "confidence_score": 0.68,
    "upper_bound": 72000,
    "lower_bound": 67000,
    "model_used": "prophet",
    "forecast_series": [
      {"timestamp": "2024-01-02T00:00:00Z", "price": 68000, "upper": 69000, "lower": 67000},
      {"timestamp": "2024-01-03T00:00:00Z", "price": 68500, "upper": 70000, "lower": 67200}
    ],
    "generated_at": "2024-01-01T12:00:00Z"
  }
}
```

### Generate New Forecast
```
POST /forecasts/{coin_id}
```

**Request:**
```json
{
  "horizon": "7d"
}
```

---

## News

### List News
```
GET /news?page=1&per_page=20&sentiment=bullish
```

Parameters:
- `page`: Page number
- `per_page`: Items per page
- `sentiment`: Filter by `bullish`, `bearish`, or `neutral`

### Get News for Coin
```
GET /news/coin/{coin_id}?page=1&per_page=20
```

### Get Sentiment Summary
```
GET /news/sentiment?coin_id=bitcoin
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_sentiment": "bullish",
    "bullish_pct": 55.5,
    "bearish_pct": 20.3,
    "neutral_pct": 24.2,
    "total_articles": 150,
    "sentiment_trend": [
      {"date": "2024-01-01", "bullish": 45, "bearish": 30, "neutral": 25},
      {"date": "2024-01-02", "bullish": 55, "bearish": 20, "neutral": 25}
    ]
  }
}
```

---

## Response Format

All endpoints follow a consistent envelope:

### Success
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 250
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Coin with ID 'invalid' not found",
    "details": {}
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `AI_AGENT_ERROR` | 502 | AI agent processing failed |
| `EXTERNAL_API_ERROR` | 502 | Upstream API failure |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Rate Limiting

- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute
- Enterprise: Custom limits

Rate limit headers are included in every response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```
