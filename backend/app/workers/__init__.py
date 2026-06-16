"""
Background job workers using ARQ (async Redis Queue).

Phase 2 will define recurring and on-demand jobs:
- price_poller.py (periodic CoinGecko price ingestion)
- news_poller.py (periodic news fetching)
- analysis_worker.py (trigger AI analysis jobs)
- forecast_worker.py (trigger forecast generation)
- notification_worker.py (send push/email alerts)
"""
