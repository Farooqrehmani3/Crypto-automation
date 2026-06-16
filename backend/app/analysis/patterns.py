"""
Chart Pattern Detection

Detects candlestick patterns: engulfing, doji, hammer, morning/evening star,
double top/bottom, head and shoulders, triangles, channels, and breakouts.
"""

from typing import Optional
import numpy as np


def detect_patterns(
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
) -> list[str]:
    """Detect all common candlestick and chart patterns."""
    patterns = []

    if len(closes) < 3:
        return patterns

    o, h, l, c = np.array(opens), np.array(highs), np.array(lows), np.array(closes)

    # Single candle patterns
    if _is_doji(o[-1], c[-1], h[-1], l[-1]):
        patterns.append("Doji")
    if _is_hammer(o[-1], c[-1], h[-1], l[-1]):
        patterns.append("Hammer")
    if _is_shooting_star(o[-1], c[-1], h[-1], l[-1]):
        patterns.append("Shooting Star")

    # Two-candle patterns
    if len(closes) >= 2:
        if _is_bullish_engulfing(o[-2], c[-2], o[-1], c[-1]):
            patterns.append("Bullish Engulfing")
        if _is_bearish_engulfing(o[-2], c[-2], o[-1], c[-1]):
            patterns.append("Bearish Engulfing")

    # Three-candle patterns
    if len(closes) >= 3:
        if _is_morning_star(o, c, -3, -2, -1):
            patterns.append("Morning Star")
        if _is_evening_star(o, c, -3, -2, -1):
            patterns.append("Evening Star")
        if _is_three_white_soldiers(o, c):
            patterns.append("Three White Soldiers")
        if _is_three_black_crows(o, c):
            patterns.append("Three Black Crows")

    # Chart patterns (need more data)
    if len(closes) >= 20:
        # Support/Resistance
        levels = _find_support_resistance(h, l, c)
        if levels.get("breakout"):
            patterns.append(f"Breakout above ${levels['resistance']:.2f}")
        if levels.get("breakdown"):
            patterns.append(f"Breakdown below ${levels['support']:.2f}")

        # Double top/bottom
        if _is_double_top(h):
            patterns.append("Double Top")
        if _is_double_bottom(l):
            patterns.append("Double Bottom")

        # Head and Shoulders
        if _is_head_shoulders(h):
            patterns.append("Head and Shoulders (Bearish)")
        if _is_inverse_head_shoulders(l):
            patterns.append("Inverse Head and Shoulders (Bullish)")

        # Trend detection
        trend = _detect_trend(c)
        if trend:
            patterns.append(trend)

    return patterns


def _is_doji(open_p: float, close: float, high: float, low: float) -> bool:
    """Doji: Open and close are nearly equal."""
    body = abs(close - open_p)
    total_range = high - low
    if total_range == 0:
        return False
    return body / total_range < 0.1


def _is_hammer(open_p: float, close: float, high: float, low: float) -> bool:
    """Hammer: Small body at top, long lower wick."""
    body = abs(close - open_p)
    if body == 0:
        return False
    upper_wick = high - max(open_p, close)
    lower_wick = min(open_p, close) - low
    return lower_wick > body * 2 and upper_wick < body * 0.5


def _is_shooting_star(open_p: float, close: float, high: float, low: float) -> bool:
    """Shooting Star: Small body at bottom, long upper wick."""
    body = abs(close - open_p)
    if body == 0:
        return False
    upper_wick = high - max(open_p, close)
    lower_wick = min(open_p, close) - low
    return upper_wick > body * 2 and lower_wick < body * 0.5


def _is_bullish_engulfing(o1: float, c1: float, o2: float, c2: float) -> bool:
    """Bullish Engulfing: Bearish candle followed by larger bullish candle."""
    return c1 < o1 and c2 > o2 and c2 > o1 and o2 < c1


def _is_bearish_engulfing(o1: float, c1: float, o2: float, c2: float) -> bool:
    """Bearish Engulfing: Bullish candle followed by larger bearish candle."""
    return c1 > o1 and c2 < o2 and c2 < o1 and o2 > c1


def _is_morning_star(o, c, i1: int, i2: int, i3: int) -> bool:
    """Morning Star: Bearish → Small → Bullish (3 candles)."""
    return c[i1] < o[i1] and abs(c[i2] - o[i2]) < abs(c[i1] - o[i1]) * 0.3 and c[i3] > o[i3]


def _is_evening_star(o, c, i1: int, i2: int, i3: int) -> bool:
    """Evening Star: Bullish → Small → Bearish (3 candles)."""
    return c[i1] > o[i1] and abs(c[i2] - o[i2]) < abs(c[i1] - o[i1]) * 0.3 and c[i3] < o[i3]


def _is_three_white_soldiers(o, c) -> bool:
    """Three consecutive bullish candles with higher closes."""
    return (
        c[-1] > o[-1]
        and c[-2] > o[-2]
        and c[-3] > o[-3]
        and c[-1] > c[-2] > c[-3]
    )


def _is_three_black_crows(o, c) -> bool:
    """Three consecutive bearish candles with lower closes."""
    return (
        c[-1] < o[-1]
        and c[-2] < o[-2]
        and c[-3] < o[-3]
        and c[-1] < c[-2] < c[-3]
    )


def _is_double_top(highs: np.ndarray) -> bool:
    """Detect double top pattern."""
    if len(highs) < 10:
        return False
    recent = highs[-10:]
    max1_idx = np.argmax(recent)
    max1 = recent[max1_idx]
    # Look for another peak of similar height at least 3 bars away
    for i in range(len(recent)):
        if abs(i - max1_idx) >= 3 and abs(recent[i] - max1) / max1 < 0.02:
            # Check for valley between them
            between = recent[min(i, max1_idx): max(i, max1_idx) + 1]
            if min(between) < max1 * 0.97:
                return True
    return False


def _is_double_bottom(lows: np.ndarray) -> bool:
    """Detect double bottom pattern."""
    if len(lows) < 10:
        return False
    recent = lows[-10:]
    min1_idx = np.argmin(recent)
    min1 = recent[min1_idx]
    for i in range(len(recent)):
        if abs(i - min1_idx) >= 3 and abs(recent[i] - min1) / min1 < 0.02:
            between = recent[min(i, min1_idx): max(i, min1_idx) + 1]
            if max(between) > min1 * 1.03:
                return True
    return False


def _is_head_shoulders(highs: np.ndarray) -> bool:
    """Simplified head and shoulders detection."""
    if len(highs) < 20:
        return False

    recent = highs[-20:]
    peaks = []
    for i in range(1, len(recent) - 1):
        if recent[i] > recent[i - 1] and recent[i] > recent[i + 1]:
            peaks.append((i, recent[i]))

    if len(peaks) >= 3:
        # Check for left shoulder, head, right shoulder pattern
        for i in range(len(peaks) - 2):
            ls, hd, rs = peaks[i], peaks[i + 1], peaks[i + 2]
            if hd[1] > ls[1] and hd[1] > rs[1] and abs(ls[1] - rs[1]) / ls[1] < 0.05:
                return True
    return False


def _is_inverse_head_shoulders(lows: np.ndarray) -> bool:
    """Simplified inverse head and shoulders detection."""
    if len(lows) < 20:
        return False

    recent = lows[-20:]
    troughs = []
    for i in range(1, len(recent) - 1):
        if recent[i] < recent[i - 1] and recent[i] < recent[i + 1]:
            troughs.append((i, recent[i]))

    if len(troughs) >= 3:
        for i in range(len(troughs) - 2):
            ls, hd, rs = troughs[i], troughs[i + 1], troughs[i + 2]
            if hd[1] < ls[1] and hd[1] < rs[1] and abs(ls[1] - rs[1]) / ls[1] < 0.05:
                return True
    return False


def _find_support_resistance(
    highs: np.ndarray, lows: np.ndarray, closes: np.ndarray
) -> dict:
    """Find key support and resistance levels, detect breakouts."""
    recent_high = np.max(highs[-20:])
    recent_low = np.min(lows[-20:])
    current = closes[-1]

    # Simple breakout detection
    result = {"support": recent_low, "resistance": recent_high}
    if current > recent_high * 1.005:
        result["breakout"] = True
    if current < recent_low * 0.995:
        result["breakdown"] = True
    return result


def _detect_trend(closes: np.ndarray) -> Optional[str]:
    """Detect market trend using moving averages."""
    if len(closes) < 20:
        return None

    sma_short = np.mean(closes[-5:])
    sma_medium = np.mean(closes[-10:])
    sma_long = np.mean(closes[-20:])

    # Check for channel
    highs = closes[-20:]
    channel_high = np.max(highs)
    channel_low = np.min(highs)

    if sma_short > sma_medium > sma_long:
        if _is_ascending_channel(highs):
            return "Ascending Channel"
        return "Uptrend"
    elif sma_short < sma_medium < sma_long:
        if _is_descending_channel(highs):
            return "Descending Channel"
        return "Downtrend"
    else:
        return "Sideways / Consolidation"


def _is_ascending_channel(data: np.ndarray) -> bool:
    """Check if price is in an ascending channel."""
    if len(data) < 10:
        return False
    first_half = np.mean(data[: len(data) // 2])
    second_half = np.mean(data[len(data) // 2:])
    return second_half > first_half * 1.02


def _is_descending_channel(data: np.ndarray) -> bool:
    """Check if price is in a descending channel."""
    if len(data) < 10:
        return False
    first_half = np.mean(data[: len(data) // 2])
    second_half = np.mean(data[len(data) // 2:])
    return second_half < first_half * 0.98
