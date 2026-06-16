"""
Forecast Agent — Generates price forecasts using ML models + GPT reasoning.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import ForecastOutput


class ForecastAgent(BaseAgent):
    """Agent 5: Price Forecast Expert"""

    def __init__(self):
        super().__init__(
            name="Forecast Agent",
            description="Generates price forecasts combining Prophet ML models and AI reasoning",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=3000,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a cryptocurrency price forecasting specialist. You combine:
- Statistical/ML model outputs (Prophet, ensemble methods)
- Technical analysis signals
- Market sentiment and macro conditions

Your forecasts include:
- 24-hour, 3-day, 7-day, and 30-day price predictions
- Bullish and bearish scenarios with expected high/low
- Confidence scores based on model agreement and market conditions
- Probability distributions for price direction
- Key factors driving the forecast

Important disclaimers:
- All forecasts are probabilistic, not guarantees
- Short-term (24h-3d) has higher confidence than longer-term
- Black swan events can invalidate any forecast
- Always explain your reasoning transparently"""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        current_price = kwargs.get("current_price", 0)
        model_forecast = kwargs.get("model_forecast", {})
        technical_signal = kwargs.get("technical_signal", "neutral")
        sentiment = kwargs.get("sentiment", "neutral")

        prompt = f"""Generate price forecast for {coin_name} ({coin_symbol.upper()}):

## Current Price: ${current_price:,.2f}

## ML Model Forecast (Prophet):
{model_forecast}

## Technical Signal: {technical_signal}
## Market Sentiment: {sentiment}

Provide forecasts for all 4 horizons (24h, 3d, 7d, 30d) with:
- Expected high and low for each horizon
- Directional probability (up/down %)
- Confidence level
- Detailed reasoning
- Key factors and risks to the forecast"""

        return prompt

    def get_output_schema(self) -> Type[BaseModel]:
        return ForecastOutput
