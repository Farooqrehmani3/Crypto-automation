"""
Risk Metrics Calculator

Computes volatility, drawdown, Sharpe/Sortino ratios, VaR, beta, and correlation.
"""

import numpy as np
from typing import Optional


def calculate_returns(prices: list[float]) -> np.ndarray:
    """Calculate daily returns from price series."""
    arr = np.array(prices)
    return (arr[1:] - arr[:-1]) / arr[:-1]


def annualized_volatility(returns: np.ndarray, periods: int = 365) -> float:
    """Annualized volatility from daily returns."""
    if len(returns) < 2:
        return 0.0
    return float(np.std(returns) * np.sqrt(periods))


def max_drawdown(prices: list[float]) -> float:
    """Maximum drawdown as a decimal (0.20 = 20% drawdown)."""
    arr = np.array(prices)
    peak = np.maximum.accumulate(arr)
    drawdown = (arr - peak) / peak
    return float(abs(np.min(drawdown)))


def sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.05,
    periods: int = 365,
) -> float:
    """Annualized Sharpe ratio."""
    if len(returns) < 2 or np.std(returns) == 0:
        return 0.0
    excess = np.mean(returns) * periods - risk_free_rate
    return float(excess / (np.std(returns) * np.sqrt(periods)))


def sortino_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.05,
    periods: int = 365,
) -> float:
    """Annualized Sortino ratio (only penalizes downside)."""
    if len(returns) < 2:
        return 0.0
    downside = returns[returns < 0]
    if len(downside) < 2 or np.std(downside) == 0:
        return 0.0
    excess = np.mean(returns) * periods - risk_free_rate
    return float(excess / (np.std(downside) * np.sqrt(periods)))


def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Historical Value at Risk at specified confidence level."""
    if len(returns) < 2:
        return 0.0
    return float(abs(np.percentile(returns, (1 - confidence) * 100)))


def conditional_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Conditional VaR (Expected Shortfall)."""
    if len(returns) < 2:
        return 0.0
    var_threshold = np.percentile(returns, (1 - confidence) * 100)
    tail = returns[returns <= var_threshold]
    if len(tail) == 0:
        return 0.0
    return float(abs(np.mean(tail)))


def beta(asset_returns: np.ndarray, market_returns: np.ndarray) -> float:
    """Calculate beta relative to market (e.g., BTC)."""
    if len(asset_returns) < 2 or len(market_returns) < 2:
        return 1.0
    min_len = min(len(asset_returns), len(market_returns))
    a = asset_returns[-min_len:]
    m = market_returns[-min_len:]
    cov = np.cov(a, m)[0][1]
    var = np.var(m)
    if var == 0:
        return 1.0
    return float(cov / var)


def correlation(asset_returns: np.ndarray, market_returns: np.ndarray) -> float:
    """Pearson correlation coefficient."""
    if len(asset_returns) < 2 or len(market_returns) < 2:
        return 0.0
    min_len = min(len(asset_returns), len(market_returns))
    a = asset_returns[-min_len:]
    m = market_returns[-min_len:]
    corr = np.corrcoef(a, m)[0][1]
    return float(corr) if not np.isnan(corr) else 0.0


def calculate_all_risk_metrics(
    prices: list[float],
    btc_prices: Optional[list[float]] = None,
) -> dict:
    """Compute all risk metrics at once."""
    if len(prices) < 30:
        return {}

    daily_returns = calculate_returns(prices)
    returns_30d = daily_returns[-30:] if len(daily_returns) >= 30 else daily_returns
    returns_90d = daily_returns[-90:] if len(daily_returns) >= 90 else daily_returns

    metrics = {
        "volatility_30d": annualized_volatility(returns_30d),
        "volatility_90d": annualized_volatility(returns_90d),
        "max_drawdown_30d": max_drawdown(prices[-30:]) if len(prices) >= 30 else 0,
        "sharpe_ratio": sharpe_ratio(daily_returns),
        "sortino_ratio": sortino_ratio(daily_returns),
        "var_95": value_at_risk(daily_returns, 0.95),
        "var_99": value_at_risk(daily_returns, 0.99),
    }

    # Beta and correlation relative to BTC
    if btc_prices and len(btc_prices) >= 30:
        btc_returns = calculate_returns(btc_prices)
        metrics["beta_vs_btc"] = beta(daily_returns, btc_returns)
        metrics["correlation_btc"] = correlation(daily_returns, btc_returns)
    else:
        metrics["beta_vs_btc"] = 1.0
        metrics["correlation_btc"] = 0.8

    return metrics
