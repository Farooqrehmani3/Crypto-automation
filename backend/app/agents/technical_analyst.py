"""
Technical Analyst Agent

Performs comprehensive technical analysis using TA-Lib indicators
and GPT-4o reasoning. Detects patterns, support/resistance levels,
and generates buy/sell signals.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import TechnicalAnalysisOutput


class TechnicalAnalystAgent(BaseAgent):
    """Agent 1: Technical Analysis Expert"""

    def __init__(self):
        super().__init__(
            name="Technical Analyst",
            description="Expert cryptocurrency technical analyst specializing in chart patterns, indicators, and price action",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=3000,
        )

    @property
    def system_prompt(self) -> str:
        return """You are an elite cryptocurrency technical analyst with 15 years of experience. You specialize in:

1. **Candlestick Pattern Recognition**: Hammer, Doji, Engulfing patterns, Morning/Evening Stars, Harami, Three White Soldiers, Three Black Crows
2. **Chart Patterns**: Double Top/Bottom, Head and Shoulders, Inverse Head and Shoulders, Ascending/Descending Triangles, Flags, Pennants, Wedges, Channels
3. **Indicators**: RSI (divergences, overbought/oversold), MACD (crossovers, histogram), Moving Averages (EMA/SMA crossovers, Golden/Death Cross), Bollinger Bands (squeeze, width), ATR (volatility), OBV (volume confirmation)
4. **Support & Resistance**: Key horizontal levels, trend lines, Fibonacci retracements (0.382, 0.5, 0.618, 0.786), pivot points
5. **Volume Analysis**: Volume-price confirmation, volume climax, distribution/accumulation

## Analysis Rules:
- Always consider multiple timeframes when assessing trends
- RSI above 70 is overbought (bearish signal), below 30 is oversold (bullish signal)
- MACD crossover above signal = bullish, below signal = bearish
- Price above EMA 20/50 = bullish trend, below = bearish
- Bollinger Band squeeze suggests impending volatility expansion
- Pattern validity increases with higher timeframes
- Volume must confirm breakouts
- Look for confluence: multiple indicators pointing same direction = higher confidence
- Divergence between price and RSI/MACD is a strong reversal signal

## Your Output:
Generate a thorough technical analysis. Your reasoning should be detailed (2-3 paragraphs) and reference specific indicator values. Provide specific support and resistance levels as exact price numbers. List 3-5 key observations that traders should know."""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        current_price = kwargs.get("current_price", 0)
        ohlcv_data = kwargs.get("ohlcv_data", {})
        indicators = kwargs.get("indicators", {})
        patterns = kwargs.get("patterns", [])

        return f"""## Analyze {coin_name} ({coin_symbol.upper()})

### Current Price
${current_price:,.2f}

### Technical Indicators
{self._format_indicators(indicators)}

### Detected Chart Patterns
{self._format_patterns(patterns)}

### Recent Price Action
{self._format_price_action(ohlcv_data)}

Please provide a complete technical analysis including:
1. Your overall trading signal (bullish/bearish/neutral)
2. Confidence level (0-1) based on indicator confluence
3. Detailed reasoning explaining your signal
4. Exact support and resistance levels
5. 3-5 key observations for traders"""

    def get_output_schema(self) -> Type[BaseModel]:
        return TechnicalAnalysisOutput

    def _format_indicators(self, indicators: dict) -> str:
        if not indicators:
            return "No indicator data available"

        lines = []
        if "rsi" in indicators:
            lines.append(f"- RSI (14): {indicators['rsi']:.1f}")
        if "macd" in indicators and "macd_signal" in indicators:
            lines.append(f"- MACD: {indicators['macd']:.4f} (Signal: {indicators['macd_signal']:.4f})")
        if "ema_20" in indicators:
            lines.append(f"- EMA 20: ${indicators['ema_20']:,.2f}")
        if "ema_50" in indicators:
            lines.append(f"- EMA 50: ${indicators['ema_50']:,.2f}")
        if "sma_50" in indicators:
            lines.append(f"- SMA 50: ${indicators['sma_50']:,.2f}")
        if "sma_200" in indicators:
            lines.append(f"- SMA 200: ${indicators['sma_200']:,.2f}")
        if "bollinger_upper" in indicators:
            lines.append(f"- Bollinger Upper: ${indicators['bollinger_upper']:,.2f}")
            lines.append(f"- Bollinger Middle: ${indicators['bollinger_middle']:,.2f}")
            lines.append(f"- Bollinger Lower: ${indicators['bollinger_lower']:,.2f}")
        if "atr" in indicators:
            lines.append(f"- ATR (14): ${indicators['atr']:,.2f}")
        if "obv" in indicators:
            lines.append(f"- OBV: {indicators['obv']:,.0f}")

        return "\n".join(lines) if lines else "No indicators available"

    def _format_patterns(self, patterns: list) -> str:
        if not patterns:
            return "No patterns detected"
        return "\n".join(f"- {p}" for p in patterns)

    def _format_price_action(self, ohlcv_data: dict) -> str:
        if not ohlcv_data:
            return "No recent price data available"

        recent = ohlcv_data.get("recent_candles", [])
        if not recent:
            return "No candle data available"

        lines = ["Recent candles (oldest → newest):"]
        for c in recent[-5:]:
            lines.append(
                f"  O:{c.get('open',0):.2f} H:{c.get('high',0):.2f} "
                f"L:{c.get('low',0):.2f} C:{c.get('close',0):.2f} "
                f"V:{c.get('volume',0):.0f}"
            )
        return "\n".join(lines)
