"""
Technical Indicators Calculator

Wraps TA-Lib for efficient indicator computation.
Provides fallback pure-python implementations when TA-Lib is unavailable.
"""

import numpy as np
from typing import Optional
from structlog import get_logger

logger = get_logger(__name__)

# Try to import TA-Lib, fall back to pure Python
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    logger.warning("TA-Lib not installed, using pure Python fallbacks")


def calculate_rsi(closes: list[float], period: int = 14) -> Optional[list[float]]:
    """Calculate Relative Strength Index."""
    if len(closes) < period + 1:
        return None

    if HAS_TALIB:
        arr = np.array(closes, dtype=np.float64)
        result = talib.RSI(arr, timeperiod=period)
        return [float(x) if not np.isnan(x) else None for x in result]

    # Pure Python fallback
    closes = np.array(closes)
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    rsi = [None] * period
    if avg_loss == 0:
        rsi.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100.0 - (100.0 / (1.0 + rs)))

    for i in range(period, len(closes) - 1):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100.0 - (100.0 / (1.0 + rs)))

    return rsi


def calculate_macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Optional[dict]:
    """Calculate MACD (Moving Average Convergence Divergence)."""
    if len(closes) < slow + signal:
        return None

    if HAS_TALIB:
        arr = np.array(closes, dtype=np.float64)
        macd, macd_signal, macd_hist = talib.MACD(
            arr, fastperiod=fast, slowperiod=slow, signalperiod=signal
        )
        return {
            "macd": [float(x) if not np.isnan(x) else None for x in macd],
            "signal": [float(x) if not np.isnan(x) else None for x in macd_signal],
            "histogram": [float(x) if not np.isnan(x) else None for x in macd_hist],
        }

    # Pure Python fallback using EMA
    closes = np.array(closes)
    ema_fast = _calculate_ema(closes, fast)
    ema_slow = _calculate_ema(closes, slow)
    macd_line = ema_fast - ema_slow
    macd_signal_line = _calculate_ema(macd_line[slow-1:], signal)
    # Pad signal line to match length
    pad = len(macd_line) - len(macd_signal_line)
    macd_signal_full = np.concatenate([np.full(pad, np.nan), macd_signal_line])
    histogram = macd_line - macd_signal_full

    return {
        "macd": [float(x) if not np.isnan(x) else None for x in macd_line],
        "signal": [float(x) if not np.isnan(x) else None for x in macd_signal_full],
        "histogram": [float(x) if not np.isnan(x) else None for x in histogram],
    }


def calculate_ema(closes: list[float], period: int) -> Optional[list[float]]:
    """Calculate Exponential Moving Average."""
    if len(closes) < period:
        return None

    if HAS_TALIB:
        arr = np.array(closes, dtype=np.float64)
        result = talib.EMA(arr, timeperiod=period)
        return [float(x) if not np.isnan(x) else None for x in result]

    return _calculate_ema(np.array(closes), period).tolist()


def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
    """Internal EMA calculator."""
    k = 2.0 / (period + 1.0)
    ema = np.zeros_like(data)
    ema[:period] = np.nan
    ema[period - 1] = np.mean(data[:period])
    for i in range(period, len(data)):
        ema[i] = data[i] * k + ema[i - 1] * (1 - k)
    return ema


def calculate_sma(closes: list[float], period: int) -> Optional[list[float]]:
    """Calculate Simple Moving Average."""
    if len(closes) < period:
        return None

    if HAS_TALIB:
        arr = np.array(closes, dtype=np.float64)
        result = talib.SMA(arr, timeperiod=period)
        return [float(x) if not np.isnan(x) else None for x in result]

    closes = np.array(closes)
    sma = np.convolve(closes, np.ones(period) / period, mode="valid")
    return [None] * (period - 1) + sma.tolist()


def calculate_bollinger_bands(
    closes: list[float],
    period: int = 20,
    nbdev: int = 2,
) -> Optional[dict]:
    """Calculate Bollinger Bands."""
    if len(closes) < period:
        return None

    if HAS_TALIB:
        arr = np.array(closes, dtype=np.float64)
        upper, middle, lower = talib.BBANDS(
            arr, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev, matype=0
        )
        return {
            "upper": [float(x) if not np.isnan(x) else None for x in upper],
            "middle": [float(x) if not np.isnan(x) else None for x in middle],
            "lower": [float(x) if not np.isnan(x) else None for x in lower],
        }

    # Pure Python
    closes = np.array(closes)
    sma = np.array(calculate_sma(closes.tolist(), period))
    rolling_std = np.array([np.nan] * len(closes))
    for i in range(period - 1, len(closes)):
        rolling_std[i] = np.std(closes[i - period + 1 : i + 1])

    upper = sma + nbdev * rolling_std
    lower = sma - nbdev * rolling_std

    return {
        "upper": upper.tolist(),
        "middle": sma.tolist(),
        "lower": lower.tolist(),
    }


def calculate_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14,
) -> Optional[list[float]]:
    """Calculate Average True Range."""
    if len(closes) < period + 1:
        return None

    if HAS_TALIB:
        h, l, c = np.array(highs), np.array(lows), np.array(closes)
        result = talib.ATR(h, l, c, timeperiod=period)
        return [float(x) if not np.isnan(x) else None for x in result]

    # Pure Python
    highs, lows, closes = np.array(highs), np.array(lows), np.array(closes)
    tr = np.zeros(len(closes))
    tr[0] = highs[0] - lows[0]
    for i in range(1, len(closes)):
        tr[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )

    atr = [None] * period
    atr.append(np.mean(tr[:period]))
    for i in range(period, len(closes)):
        atr.append((atr[i - 1] * (period - 1) + tr[i]) / period)

    return atr


def calculate_all_indicators(
    closes: list[float],
    highs: list[float] = None,
    lows: list[float] = None,
    volumes: list[float] = None,
) -> dict:
    """Calculate all commonly used indicators at once."""
    if highs is None:
        highs = closes
    if lows is None:
        lows = closes

    result = {}

    # RSI
    rsi = calculate_rsi(closes)
    if rsi:
        result["rsi"] = rsi[-1] if rsi[-1] is not None else None

    # MACD
    macd_data = calculate_macd(closes)
    if macd_data:
        macd_vals = [x for x in macd_data["macd"] if x is not None]
        sig_vals = [x for x in macd_data["signal"] if x is not None]
        hist_vals = [x for x in macd_data["histogram"] if x is not None]
        if macd_vals and sig_vals and hist_vals:
            result["macd"] = macd_vals[-1]
            result["macd_signal"] = sig_vals[-1]
            result["macd_histogram"] = hist_vals[-1]

    # MAs
    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    sma50 = calculate_sma(closes, 50)
    sma200 = calculate_sma(closes, 200)

    if ema20:
        result["ema_20"] = ema20[-1]
    if ema50:
        result["ema_50"] = ema50[-1]
    if sma50:
        result["sma_50"] = sma50[-1]
    if sma200:
        result["sma_200"] = sma200[-1]

    # Bollinger Bands
    bb = calculate_bollinger_bands(closes)
    if bb:
        upper_vals = [x for x in bb["upper"] if x is not None]
        mid_vals = [x for x in bb["middle"] if x is not None]
        low_vals = [x for x in bb["lower"] if x is not None]
        if upper_vals and mid_vals and low_vals:
            result["bollinger_upper"] = upper_vals[-1]
            result["bollinger_middle"] = mid_vals[-1]
            result["bollinger_lower"] = low_vals[-1]

    # ATR
    if highs is not None and lows is not None:
        atr = calculate_atr(highs, lows, closes)
        if atr:
            atr_vals = [x for x in atr if x is not None]
            if atr_vals:
                result["atr"] = atr_vals[-1]

    return result
