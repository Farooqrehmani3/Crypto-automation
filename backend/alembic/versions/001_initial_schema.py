"""Initial schema — create all core tables

Revision ID: 001
Revises:
Create Date: 2026-06-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enable pgcrypto extension for gen_random_uuid() ──────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ══════════════════════════════════════════════════════════════════════
    # 1. coins
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "coins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("coingecko_id", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("symbol", sa.String(20), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("market_cap_rank", sa.Integer(), nullable=True),
        sa.Column("current_price_usd", sa.Float(), nullable=True),
        sa.Column("market_cap_usd", sa.Float(), nullable=True),
        sa.Column("total_volume_usd", sa.Float(), nullable=True),
        sa.Column("circulating_supply", sa.Float(), nullable=True),
        sa.Column("total_supply", sa.Float(), nullable=True),
        sa.Column("max_supply", sa.Float(), nullable=True),
        sa.Column("ath_usd", sa.Float(), nullable=True),
        sa.Column("atl_usd", sa.Float(), nullable=True),
        sa.Column("high_24h_usd", sa.Float(), nullable=True),
        sa.Column("low_24h_usd", sa.Float(), nullable=True),
        sa.Column("price_change_24h_percent", sa.Float(), nullable=True),
        sa.Column("price_change_7d_percent", sa.Float(), nullable=True),
        sa.Column("price_change_30d_percent", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("genesis_date", sa.Date(), nullable=True),
        sa.Column("homepage_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_coins_market_cap_rank", "coins", ["market_cap_rank"])
    op.create_index("ix_coins_symbol_name", "coins", ["symbol", "name"])
    op.create_check_constraint(
        "ck_coins_market_cap_rank_positive",
        "coins",
        "market_cap_rank IS NULL OR market_cap_rank > 0",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 2. coin_prices
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "coin_prices",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("price_usd", sa.Float(), nullable=False),
        sa.Column("market_cap_usd", sa.Float(), nullable=True),
        sa.Column("volume_usd", sa.Float(), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default=sa.text("'coingecko'")),
    )

    op.create_unique_constraint("uq_coin_price_timestamp", "coin_prices", ["coin_id", "timestamp"])
    op.create_index("ix_coin_prices_coin_timestamp", "coin_prices", ["coin_id", "timestamp"])
    op.create_index("ix_coin_prices_timestamp_btree", "coin_prices", [sa.text("timestamp DESC")])

    # ══════════════════════════════════════════════════════════════════════
    # 3. watchlists
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "watchlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(100), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_unique_constraint("uq_watchlist_user_name", "watchlists", ["user_id", "name"])
    op.create_index("ix_watchlists_user_default", "watchlists", ["user_id", "is_default"])

    # ══════════════════════════════════════════════════════════════════════
    # 4. watchlist_items
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "watchlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("watchlist_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("watchlists.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("added_price_usd", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
    )

    op.create_unique_constraint("uq_watchlist_item_coin", "watchlist_items",
                                ["watchlist_id", "coin_id"])

    # ══════════════════════════════════════════════════════════════════════
    # 5. portfolios
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(100), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("total_value_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_cost_basis_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_pnl_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_unique_constraint("uq_portfolio_user_name", "portfolios", ["user_id", "name"])
    op.create_index("ix_portfolios_user_default", "portfolios", ["user_id", "is_default"])

    # ══════════════════════════════════════════════════════════════════════
    # 6. portfolio_assets
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "portfolio_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="RESTRICT"),
                  nullable=False, index=True),
        sa.Column("quantity", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("average_cost_basis_usd", sa.Float(), nullable=False,
                  server_default=sa.text("0")),
        sa.Column("current_value_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("pnl_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("pnl_percent", sa.Float(), nullable=False, server_default=sa.text("0")),
    )

    op.create_unique_constraint("uq_portfolio_asset_coin", "portfolio_assets",
                                ["portfolio_id", "coin_id"])
    op.create_check_constraint(
        "ck_portfolio_asset_quantity_nonnegative",
        "portfolio_assets",
        "quantity >= 0",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 7. portfolio_transactions
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "portfolio_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="RESTRICT"),
                  nullable=False, index=True),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price_per_coin_usd", sa.Float(), nullable=False),
        sa.Column("total_value_usd", sa.Float(), nullable=False),
        sa.Column("fee_usd", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
    )

    op.create_index("ix_transactions_portfolio_date", "portfolio_transactions",
                    ["portfolio_id", "transaction_date"])
    op.create_check_constraint(
        "ck_transaction_quantity_positive",
        "portfolio_transactions",
        "quantity > 0",
    )
    op.create_check_constraint(
        "ck_transaction_type_valid",
        "portfolio_transactions",
        "transaction_type IN ('buy', 'sell', 'transfer_in', 'transfer_out')",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 8. user_preferences
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("currency", sa.String(10), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("language", sa.String(10), nullable=False, server_default=sa.text("'en'")),
        sa.Column("email_notifications", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("push_notifications", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("price_alert_threshold_percent", sa.Float(), nullable=False,
                  server_default=sa.text("5.0")),
        sa.Column("breaking_news_alerts", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("ai_analysis_alerts", sa.Boolean(), nullable=False,
                  server_default=sa.text("true")),
        sa.Column("default_watchlist_id", sa.String(36), nullable=True),
        sa.Column("default_portfolio_id", sa.String(36), nullable=True),
        sa.Column("dashboard_layout", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("favorite_coins", postgresql.JSONB(), nullable=True),
        sa.Column("theme", sa.String(20), nullable=False, server_default=sa.text("'system'")),
        sa.Column("chart_preferences", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_user_prefs_user_id", "user_preferences", ["user_id"])

    # ══════════════════════════════════════════════════════════════════════
    # 9. news_articles
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "news_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("external_id", sa.String(255), unique=True, nullable=True, index=True),
        sa.Column("source", sa.String(100), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("author", sa.String(200), nullable=True),
        sa.Column("image_url", sa.String(2000), nullable=True),
        sa.Column("published_at", sa.String(), nullable=False, index=True),
        sa.Column("language", sa.String(10), nullable=False, server_default=sa.text("'en'")),
        sa.Column("categories", sa.String(500), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_news_published_source", "news_articles", ["published_at", "source"])
    op.create_index(
        "ix_news_is_breaking",
        "news_articles",
        ["is_breaking"],
        postgresql_where=sa.text("is_breaking = true"),
    )

    # ══════════════════════════════════════════════════════════════════════
    # 10. news_coins
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "news_coins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("news_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("news_articles.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("mention_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )

    op.create_unique_constraint("uq_news_coin", "news_coins", ["news_id", "coin_id"])

    # ══════════════════════════════════════════════════════════════════════
    # 11. news_sentiments
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "news_sentiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("news_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("news_articles.id", ondelete="CASCADE"),
                  nullable=False, unique=True, index=True),
        sa.Column("overall_sentiment", sa.String(20), nullable=False),
        sa.Column("sentiment_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_points", sa.Text(), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
    )

    op.create_check_constraint(
        "ck_sentiment_score_range",
        "news_sentiments",
        "sentiment_score >= -1.0 AND sentiment_score <= 1.0",
    )
    op.create_check_constraint(
        "ck_sentiment_valid",
        "news_sentiments",
        "overall_sentiment IN ('positive', 'negative', 'neutral')",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 12. analysis_logs
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "analysis_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="SET NULL"),
                  nullable=True, index=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("input_data_hash", sa.String(64), nullable=True),
        sa.Column("output_data", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("is_cached", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_index("ix_analysis_logs_coin_type", "analysis_logs", ["coin_id", "analysis_type"])
    op.create_index("ix_analysis_logs_created_at", "analysis_logs", ["created_at"])
    op.create_check_constraint(
        "ck_analysis_confidence_range",
        "analysis_logs",
        "confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 13. ai_predictions
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "ai_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("analysis_log_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("analysis_logs.id", ondelete="SET NULL"),
                  nullable=True, index=True),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prediction_type", sa.String(50), nullable=False),
        sa.Column("target_timeframe", sa.String(20), nullable=False),
        sa.Column("predicted_value", sa.Float(), nullable=True),
        sa.Column("predicted_direction", sa.String(10), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("prediction_metadata", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("prediction_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_index("ix_predictions_coin_timeframe", "ai_predictions",
                    ["coin_id", "target_timeframe"])
    op.create_index("ix_predictions_created_at", "ai_predictions", ["created_at"])
    op.create_check_constraint(
        "ck_prediction_confidence_range",
        "ai_predictions",
        "confidence_score >= 0.0 AND confidence_score <= 1.0",
    )

    # ══════════════════════════════════════════════════════════════════════
    # 14. coin_forecasts
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "coin_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("coin_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("coins.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("forecast_type", sa.String(50), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False),
        sa.Column("forecast_points", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("confidence_interval", sa.Float(), nullable=False,
                  server_default=sa.text("0.95")),
        sa.Column("metrics", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index("ix_forecasts_coin_horizon", "coin_forecasts", ["coin_id", "horizon_days"])
    op.create_index("ix_forecasts_generated_at", "coin_forecasts", ["generated_at"])

    # ══════════════════════════════════════════════════════════════════════
    # 15. market_snapshots
    # ══════════════════════════════════════════════════════════════════════
    op.create_table(
        "market_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("snapshot_type", sa.String(50), nullable=False),
        sa.Column("total_market_cap_usd", sa.Float(), nullable=False),
        sa.Column("total_volume_24h_usd", sa.Float(), nullable=False),
        sa.Column("btc_dominance_percent", sa.Float(), nullable=False),
        sa.Column("eth_dominance_percent", sa.Float(), nullable=True),
        sa.Column("active_cryptocurrencies", sa.Integer(), nullable=True),
        sa.Column("fear_greed_index", sa.Integer(), nullable=True),
        sa.Column("fear_greed_classification", sa.String(50), nullable=True),
        sa.Column("top_gainers", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("top_losers", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("snapshot_metadata", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_index("ix_snapshots_type_created", "market_snapshots",
                    ["snapshot_type", "created_at"])
    op.create_check_constraint(
        "ck_fear_greed_range",
        "market_snapshots",
        "fear_greed_index IS NULL OR (fear_greed_index >= 0 AND fear_greed_index <= 100)",
    )

    # ── Triggers: auto-update updated_at ──────────────────────────────────────

    _create_updated_at_trigger(op, "watchlists")
    _create_updated_at_trigger(op, "portfolios")
    _create_updated_at_trigger(op, "user_preferences")
    _create_updated_at_trigger(op, "news_articles")
    _create_updated_at_trigger(op, "analysis_logs")
    _create_updated_at_trigger(op, "ai_predictions")
    _create_updated_at_trigger(op, "market_snapshots")


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""

    _drop_updated_at_trigger(op, "market_snapshots")
    _drop_updated_at_trigger(op, "ai_predictions")
    _drop_updated_at_trigger(op, "analysis_logs")
    _drop_updated_at_trigger(op, "news_articles")
    _drop_updated_at_trigger(op, "user_preferences")
    _drop_updated_at_trigger(op, "portfolios")
    _drop_updated_at_trigger(op, "watchlists")

    op.drop_table("market_snapshots")
    op.drop_table("coin_forecasts")
    op.drop_table("ai_predictions")
    op.drop_table("analysis_logs")
    op.drop_table("news_sentiments")
    op.drop_table("news_coins")
    op.drop_table("news_articles")
    op.drop_table("user_preferences")
    op.drop_table("portfolio_transactions")
    op.drop_table("portfolio_assets")
    op.drop_table("portfolios")
    op.drop_table("watchlist_items")
    op.drop_table("watchlists")
    op.drop_table("coin_prices")
    op.drop_table("coins")


# ── Helper functions ──────────────────────────────────────────────────────────


def _create_updated_at_trigger(op_obj, table_name: str) -> None:
    """Create a BEFORE UPDATE trigger that sets updated_at to now()."""
    trigger_func = f"""
    CREATE OR REPLACE FUNCTION trg_{table_name}_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    op_obj.execute(trigger_func)

    trigger_sql = f"""
    CREATE TRIGGER trg_{table_name}_updated_at
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        EXECUTE FUNCTION trg_{table_name}_updated_at();
    """
    op_obj.execute(trigger_sql)


def _drop_updated_at_trigger(op_obj, table_name: str) -> None:
    """Drop the updated_at trigger and function for a table."""
    op_obj.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_updated_at ON {table_name}")
    op_obj.execute(f"DROP FUNCTION IF EXISTS trg_{table_name}_updated_at()")
