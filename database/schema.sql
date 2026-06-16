-- ============================================================================
-- Crypto Intelligence AI — Complete PostgreSQL Schema
-- Run this in Supabase SQL Editor (or any PostgreSQL 16+ instance)
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";          -- For text search on coin names/symbols

-- ============================================================================
-- HELPER: Auto-updating updated_at trigger
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE 1: user_preferences
-- ============================================================================
CREATE TABLE user_preferences (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE,  -- FK to auth.users (Supabase managed)
    default_timeframe       VARCHAR(10) NOT NULL DEFAULT '1d',
    default_chart_type      VARCHAR(20) NOT NULL DEFAULT 'candlestick',
    theme                   VARCHAR(10) NOT NULL DEFAULT 'system',
    notifications_enabled   BOOLEAN NOT NULL DEFAULT TRUE,
    ai_analysis_auto        BOOLEAN NOT NULL DEFAULT FALSE,
    favorite_indicators     JSONB NOT NULL DEFAULT '["RSI","MACD","EMA"]'::JSONB,
    risk_tolerance          VARCHAR(20) NOT NULL DEFAULT 'moderate',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE 2: coins
-- ============================================================================
CREATE TABLE coins (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id             VARCHAR(50) NOT NULL UNIQUE,       -- CoinGecko ID e.g. "bitcoin"
    symbol              VARCHAR(20) NOT NULL,              -- e.g. "btc"
    name                VARCHAR(100) NOT NULL,             -- e.g. "Bitcoin"
    image_url           TEXT,
    market_cap_rank     INTEGER,
    current_price       DECIMAL(24,8),
    market_cap          DECIMAL(26,2),
    total_volume        DECIMAL(26,2),
    price_change_24h    DECIMAL(12,2),
    price_change_pct_24h DECIMAL(8,4),
    price_change_pct_7d  DECIMAL(8,4),
    price_change_pct_30d DECIMAL(8,4),
    circulating_supply  DECIMAL(26,2),
    total_supply        DECIMAL(26,2),
    max_supply          DECIMAL(26,2),
    ath                 DECIMAL(24,8),
    ath_date            TIMESTAMPTZ,
    atl                 DECIMAL(24,8),
    atl_date            TIMESTAMPTZ,
    sparkline_7d        JSONB,                            -- Array of floats for sparkline
    last_updated        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_coins_updated_at
    BEFORE UPDATE ON coins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_coins_market_cap_rank ON coins(market_cap_rank);
CREATE INDEX idx_coins_symbol ON coins(symbol);
CREATE INDEX idx_coins_name_trgm ON coins USING GIN (name gin_trgm_ops);
CREATE INDEX idx_coins_symbol_trgm ON coins USING GIN (symbol gin_trgm_ops);

-- ============================================================================
-- TABLE 3: coin_prices (Time-series OHLCV data)
-- ============================================================================
CREATE TABLE coin_prices (
    id          BIGSERIAL PRIMARY KEY,
    coin_id     UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    timestamp   TIMESTAMPTZ NOT NULL,
    timeframe   VARCHAR(10) NOT NULL,          -- '1m','5m','15m','1h','4h','1d','1w'
    open        DECIMAL(24,8) NOT NULL,
    high        DECIMAL(24,8) NOT NULL,
    low         DECIMAL(24,8) NOT NULL,
    close       DECIMAL(24,8) NOT NULL,
    volume      DECIMAL(26,2) NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Unique constraint: one candle per coin+timestamp+timeframe
    UNIQUE (coin_id, timestamp, timeframe)
);

-- Critical composite index for time-series queries
CREATE INDEX idx_coin_prices_lookup
    ON coin_prices (coin_id, timeframe, timestamp DESC);

-- BRIN index for efficient range scans on large time-series data
CREATE INDEX idx_coin_prices_timestamp_brin
    ON coin_prices USING BRIN (timestamp);

-- ============================================================================
-- TABLE 4: watchlists
-- ============================================================================
CREATE TABLE watchlists (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL,                        -- FK to auth.users
    name        VARCHAR(100) NOT NULL DEFAULT 'Default',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)
);

CREATE TRIGGER trg_watchlists_updated_at
    BEFORE UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);

-- ============================================================================
-- TABLE 5: watchlist_items
-- ============================================================================
CREATE TABLE watchlist_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id    UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    coin_id         UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    is_favorite     BOOLEAN NOT NULL DEFAULT FALSE,
    added_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (watchlist_id, coin_id)
);

CREATE INDEX idx_watchlist_items_wl ON watchlist_items(watchlist_id);
CREATE INDEX idx_watchlist_items_wl_added ON watchlist_items(watchlist_id, added_at DESC);

-- ============================================================================
-- TABLE 6: portfolios
-- ============================================================================
CREATE TABLE portfolios (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,                -- FK to auth.users
    name                VARCHAR(100) NOT NULL DEFAULT 'Main Portfolio',
    total_value_usd     DECIMAL(26,2) NOT NULL DEFAULT 0,
    total_cost_basis_usd DECIMAL(26,2) NOT NULL DEFAULT 0,
    total_pnl_usd       DECIMAL(26,2) NOT NULL DEFAULT 0,
    total_pnl_pct       DECIMAL(10,4) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);

-- ============================================================================
-- TABLE 7: portfolio_assets
-- ============================================================================
CREATE TABLE portfolio_assets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id        UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    coin_id             UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    quantity            DECIMAL(24,8) NOT NULL,
    average_buy_price   DECIMAL(24,8) NOT NULL,
    cost_basis_usd      DECIMAL(26,2) NOT NULL,           -- quantity * average_buy_price
    current_value_usd   DECIMAL(26,2),                    -- Updated by worker
    pnl_usd             DECIMAL(26,2),                    -- current_value - cost_basis
    pnl_pct             DECIMAL(10,4),                    -- (current_value - cost_basis) / cost_basis * 100
    last_synced_at      TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (portfolio_id, coin_id)
);

CREATE TRIGGER trg_portfolio_assets_updated_at
    BEFORE UPDATE ON portfolio_assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX idx_portfolio_assets_portfolio ON portfolio_assets(portfolio_id);

-- ============================================================================
-- TABLE 8: portfolio_transactions
-- ============================================================================
CREATE TABLE portfolio_transactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_asset_id  UUID NOT NULL REFERENCES portfolio_assets(id) ON DELETE CASCADE,
    type                VARCHAR(10) NOT NULL CHECK (type IN ('buy', 'sell', 'transfer_in', 'transfer_out')),
    quantity            DECIMAL(24,8) NOT NULL,
    price_per_unit      DECIMAL(24,8) NOT NULL,
    total_value         DECIMAL(26,2) NOT NULL,           -- quantity * price_per_unit
    fee                 DECIMAL(26,2) NOT NULL DEFAULT 0,
    notes               TEXT,
    transaction_date    TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_portfolio_tx_asset ON portfolio_transactions(portfolio_asset_id, transaction_date DESC);

-- ============================================================================
-- TABLE 9: news
-- ============================================================================
CREATE TABLE news (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          VARCHAR(100) NOT NULL,           -- 'CryptoPanic', 'CoinDesk', 'CoinTelegraph'
    source_url      TEXT UNIQUE,
    title           VARCHAR(500) NOT NULL,
    content         TEXT,
    summary         TEXT,                            -- AI-generated summary
    image_url       TEXT,
    published_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_news_published_at ON news(published_at DESC);
CREATE INDEX idx_news_source ON news(source);

-- ============================================================================
-- TABLE 10: news_coins (junction: news <-> coins)
-- ============================================================================
CREATE TABLE news_coins (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    news_id         UUID NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    coin_id         UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    relevance_score DECIMAL(5,4) NOT NULL DEFAULT 1.0,  -- AI relevance ranking
    UNIQUE (news_id, coin_id)
);

CREATE INDEX idx_news_coins_news ON news_coins(news_id);
CREATE INDEX idx_news_coins_coin ON news_coins(coin_id);

-- ============================================================================
-- TABLE 11: news_sentiment
-- ============================================================================
CREATE TABLE news_sentiment (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    news_id             UUID NOT NULL UNIQUE REFERENCES news(id) ON DELETE CASCADE,
    sentiment           VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'bearish', 'neutral')),
    confidence_score    DECIMAL(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    analysis_text       TEXT,                       -- AI reasoning
    analyzed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_news_sentiment_type ON news_sentiment(sentiment, confidence_score DESC);

-- ============================================================================
-- TABLE 12: coin_forecasts
-- ============================================================================
CREATE TABLE coin_forecasts (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id             UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    forecast_horizon    VARCHAR(10) NOT NULL CHECK (forecast_horizon IN ('24h', '3d', '7d', '30d')),
    predicted_price     DECIMAL(24,8),
    predicted_direction VARCHAR(10) CHECK (predicted_direction IN ('up', 'down', 'sideways')),
    confidence_score    DECIMAL(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    upper_bound         DECIMAL(24,8),              -- Confidence interval upper
    lower_bound         DECIMAL(24,8),              -- Confidence interval lower
    model_used          VARCHAR(50),                -- 'prophet', 'lstm', 'ensemble'
    forecast_series     JSONB,                      -- [{timestamp, price, upper, lower}]
    generated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until         TIMESTAMPTZ NOT NULL         -- When forecast expires
);

CREATE INDEX idx_forecasts_coin_horizon ON coin_forecasts(coin_id, forecast_horizon, generated_at DESC);

-- ============================================================================
-- TABLE 13: ai_predictions
-- ============================================================================
CREATE TABLE ai_predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id             UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    analysis_id         UUID NOT NULL,              -- Groups all agent outputs from a single run
    agent_type          VARCHAR(50) NOT NULL CHECK (agent_type IN (
                            'technical', 'news', 'macro', 'sentiment',
                            'forecast', 'risk', 'report'
                        )),
    prediction_data     JSONB NOT NULL,             -- Structured output from agent
    confidence_score    DECIMAL(5,4),
    reasoning           TEXT,                        -- AI natural language reasoning
    model_version       VARCHAR(30),                -- GPT model version used
    tokens_used         INTEGER,                    -- For cost tracking
    processing_time_ms  INTEGER,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_pred_coin_agent ON ai_predictions(coin_id, agent_type, created_at DESC);
CREATE INDEX idx_ai_pred_analysis ON ai_predictions(analysis_id);

-- ============================================================================
-- TABLE 14: analysis_logs
-- ============================================================================
CREATE TABLE analysis_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL,                  -- FK to auth.users
    coin_id         UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    analysis_id     UUID NOT NULL UNIQUE,           -- Links to ai_predictions
    status          VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN (
                        'pending', 'running', 'completed', 'failed'
                    )),
    error_message   TEXT,
    duration_ms     INTEGER,
    total_api_cost  DECIMAL(10,6),                   -- Sum of all OpenAI costs for this run
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_analysis_logs_user ON analysis_logs(user_id, created_at DESC);
CREATE INDEX idx_analysis_logs_coin ON analysis_logs(coin_id, created_at DESC);

-- ============================================================================
-- TABLE 15: market_snapshots
-- ============================================================================
CREATE TABLE market_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_type   VARCHAR(30) NOT NULL CHECK (snapshot_type IN (
                        'global', 'trending', 'gainers', 'losers', 'fear_greed'
                    )),
    data            JSONB NOT NULL,
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_market_snapshots_type ON market_snapshots(snapshot_type, captured_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE coins ENABLE ROW LEVEL SECURITY;
ALTER TABLE coin_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE news ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_coins ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_sentiment ENABLE ROW LEVEL SECURITY;
ALTER TABLE coin_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_snapshots ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PUBLIC READ POLICIES (anyone can SELECT, only service_role can INSERT/UPDATE/DELETE)
-- ============================================================================

CREATE POLICY "Public read access for coins"
    ON coins FOR SELECT USING (true);

CREATE POLICY "Public read access for coin_prices"
    ON coin_prices FOR SELECT USING (true);

CREATE POLICY "Public read access for news"
    ON news FOR SELECT USING (true);

CREATE POLICY "Public read access for news_coins"
    ON news_coins FOR SELECT USING (true);

CREATE POLICY "Public read access for news_sentiment"
    ON news_sentiment FOR SELECT USING (true);

CREATE POLICY "Public read access for coin_forecasts"
    ON coin_forecasts FOR SELECT USING (true);

CREATE POLICY "Public read access for ai_predictions"
    ON ai_predictions FOR SELECT USING (true);

CREATE POLICY "Public read access for market_snapshots"
    ON market_snapshots FOR SELECT USING (true);

-- ============================================================================
-- USER-OWNED DATA POLICIES
-- ============================================================================

-- user_preferences: Users can only access their own preferences
CREATE POLICY "Users manage own preferences"
    ON user_preferences
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- watchlists: Users manage their own watchlists
CREATE POLICY "Users manage own watchlists"
    ON watchlists
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- watchlist_items: Users manage items in their watchlists (via join)
CREATE POLICY "Users manage own watchlist items"
    ON watchlist_items
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM watchlists w
            WHERE w.id = watchlist_items.watchlist_id
            AND w.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM watchlists w
            WHERE w.id = watchlist_items.watchlist_id
            AND w.user_id = auth.uid()
        )
    );

-- portfolios: Users manage their own portfolios
CREATE POLICY "Users manage own portfolios"
    ON portfolios
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- portfolio_assets: Users manage assets in their portfolios (via join)
CREATE POLICY "Users manage own portfolio assets"
    ON portfolio_assets
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM portfolios p
            WHERE p.id = portfolio_assets.portfolio_id
            AND p.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM portfolios p
            WHERE p.id = portfolio_assets.portfolio_id
            AND p.user_id = auth.uid()
        )
    );

-- portfolio_transactions: Users manage transactions for their assets (via join)
CREATE POLICY "Users manage own transactions"
    ON portfolio_transactions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM portfolio_assets pa
            JOIN portfolios p ON p.id = pa.portfolio_id
            WHERE pa.id = portfolio_transactions.portfolio_asset_id
            AND p.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM portfolio_assets pa
            JOIN portfolios p ON p.id = pa.portfolio_id
            WHERE pa.id = portfolio_transactions.portfolio_asset_id
            AND p.user_id = auth.uid()
        )
    );

-- analysis_logs: Users can only see their own analysis runs
CREATE POLICY "Users manage own analysis logs"
    ON analysis_logs
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- SERVICE ROLE POLICIES (for backend write access)
-- ============================================================================

-- The backend uses the service_role key, which bypasses RLS entirely.
-- No additional policies needed for write operations from the backend.

-- ============================================================================
-- SUPABASE REALTIME SETUP
-- ============================================================================
-- Enable realtime for tables that need live updates
ALTER PUBLICATION supabase_realtime ADD TABLE coins;
ALTER PUBLICATION supabase_realtime ADD TABLE coin_prices;
ALTER PUBLICATION supabase_realtime ADD TABLE watchlist_items;

-- ============================================================================
-- SEED DATA: Top 20 Cryptocurrencies
-- ============================================================================
INSERT INTO coins (coin_id, symbol, name, market_cap_rank) VALUES
    ('bitcoin', 'btc', 'Bitcoin', 1),
    ('ethereum', 'eth', 'Ethereum', 2),
    ('tether', 'usdt', 'Tether', 3),
    ('binancecoin', 'bnb', 'BNB', 4),
    ('solana', 'sol', 'Solana', 5),
    ('ripple', 'xrp', 'XRP', 6),
    ('usd-coin', 'usdc', 'USD Coin', 7),
    ('staked-ether', 'steth', 'Lido Staked Ether', 8),
    ('cardano', 'ada', 'Cardano', 9),
    ('dogecoin', 'doge', 'Dogecoin', 10),
    ('avalanche-2', 'avax', 'Avalanche', 11),
    ('tron', 'trx', 'TRON', 12),
    ('polkadot', 'dot', 'Polkadot', 13),
    ('chainlink', 'link', 'Chainlink', 14),
    ('matic-network', 'matic', 'Polygon', 15),
    ('wrapped-bitcoin', 'wbtc', 'Wrapped Bitcoin', 16),
    ('shiba-inu', 'shib', 'Shiba Inu', 17),
    ('litecoin', 'ltc', 'Litecoin', 18),
    ('uniswap', 'uni', 'Uniswap', 19),
    ('near', 'near', 'NEAR Protocol', 20)
ON CONFLICT (coin_id) DO NOTHING;

-- ============================================================================
-- DONE
-- ============================================================================
