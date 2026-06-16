"""
Macro Economic Analyst Agent — Analyzes macroeconomic factors affecting crypto.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import MacroAnalysisOutput


class MacroAnalystAgent(BaseAgent):
    """Agent 4: Macro Economic Analysis Expert"""

    def __init__(self):
        super().__init__(
            name="Macro Economic Analyst",
            description="Analyzes Federal Reserve policy, interest rates, CPI, regulations, and global events",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=2500,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a macroeconomic analyst specializing in cryptocurrency markets. Your expertise:
- Federal Reserve monetary policy (interest rates, quantitative tightening/easing, FOMC statements)
- Inflation data (CPI, PCE, PPI) and its impact on risk assets
- Employment data (non-farm payrolls, unemployment rate)
- Global economic conditions (GDP growth, recession risks)
- Geopolitical events (wars, sanctions, trade disputes)
- Cryptocurrency regulation (SEC, CFTC, EU MiCA, global frameworks)
- ETF flows and institutional adoption trends
- Dollar strength (DXY) and its inverse relationship with crypto

Key relationships:
- Lower rates / dovish Fed = bullish for crypto (risk-on)
- Higher rates / hawkish Fed = bearish for crypto (risk-off)
- Weak DXY = bullish for crypto
- Regulatory clarity = bullish long-term
- Institutional ETF inflows = bullish
- Banking crisis = mixed (flight to safety vs crypto as alternative)"""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        macro_data = kwargs.get("macro_data", {})

        prompt = f"""Analyze macroeconomic factors affecting {coin_name} ({coin_symbol.upper()}):

## Current Macro Environment
{macro_data.get('summary', 'Using general knowledge of current conditions.')}

## Key Data Points
- Federal Funds Rate: {macro_data.get('fed_rate', 'Check latest')}
- CPI (YoY): {macro_data.get('cpi', 'Check latest')}
- DXY: {macro_data.get('dxy', 'Check latest')}
- Bitcoin ETF Flows: {macro_data.get('etf_flows', 'Check latest')}
- Regulatory Updates: {macro_data.get('regulatory', 'Check latest')}

Provide comprehensive macro analysis with crypto market implications."""

        return prompt

    def get_output_schema(self) -> Type[BaseModel]:
        return MacroAnalysisOutput
