"""
Risk Analyst Agent — Evaluates investment risk using quantitative metrics.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import RiskAnalysisOutput


class RiskAnalystAgent(BaseAgent):
    """Agent 6: Risk Assessment Expert"""

    def __init__(self):
        super().__init__(
            name="Risk Analyst",
            description="Quantitative risk analyst evaluating volatility, VaR, drawdowns, and correlation risks",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=2500,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a quantitative risk analyst for cryptocurrency investments. Your assessment covers:

1. **Volatility**: 30-day and 90-day annualized volatility. Crypto typically 60-100%+ annualized.
2. **Value at Risk (VaR)**: Maximum expected loss at 95% and 99% confidence levels over 1-day horizon.
3. **Maximum Drawdown**: Largest peak-to-trough decline in the period.
4. **Sharpe Ratio**: Risk-adjusted return metric (>1.0 = good, >2.0 = excellent, <0.5 = poor).
5. **Sortino Ratio**: Like Sharpe but only penalizes downside volatility.
6. **Beta & Correlation**: Relative to Bitcoin — measures systematic vs idiosyncratic risk.
7. **Liquidity Risk**: Trading volume analysis, bid-ask spread considerations.

Risk scoring (0-100):
- 0-25: Low risk (stable, high liquidity, low volatility)
- 25-50: Moderate risk
- 50-75: High risk
- 75-100: Extreme risk (highly speculative, low liquidity)

Always mention position sizing recommendations relative to risk tolerance."""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        risk_metrics = kwargs.get("risk_metrics", {})

        prompt = f"""Assess investment risk for {coin_name} ({coin_symbol.upper()}):

## Computed Risk Metrics:
- 30-Day Annualized Volatility: {risk_metrics.get('volatility_30d', 'N/A')}
- 90-Day Annualized Volatility: {risk_metrics.get('volatility_90d', 'N/A')}
- Max Drawdown (30d): {risk_metrics.get('max_drawdown_30d', 'N/A')}
- Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 'N/A')}
- Sortino Ratio: {risk_metrics.get('sortino_ratio', 'N/A')}
- VaR (95%): {risk_metrics.get('var_95', 'N/A')}
- VaR (99%): {risk_metrics.get('var_99', 'N/A')}
- Beta vs BTC: {risk_metrics.get('beta_vs_btc', 'N/A')}
- Correlation with BTC: {risk_metrics.get('correlation_btc', 'N/A')}

Provide complete risk assessment with risk score, level, and detailed reasoning."""

        return prompt

    def get_output_schema(self) -> Type[BaseModel]:
        return RiskAnalysisOutput
