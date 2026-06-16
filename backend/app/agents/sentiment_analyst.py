"""
Sentiment Analyst Agent — Aggregates social media and news sentiment signals.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import SentimentAnalysisOutput


class SentimentAnalystAgent(BaseAgent):
    """Agent 3: Market Sentiment Analysis Expert"""

    def __init__(self):
        super().__init__(
            name="Sentiment Analyst",
            description="Aggregates sentiment signals from news, social media, and on-chain data",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2500,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a cryptocurrency market sentiment analyst. You aggregate signals from multiple sources:

1. **News Sentiment**: Aggregated from news articles about the coin
2. **Social Media**: Twitter/X, Reddit, Telegram sentiment signals
3. **Market Data**: Fear & Greed Index, Long/Short ratios, funding rates
4. **On-Chain**: Exchange flows, whale activity, active addresses trends

Your analysis should:
- Weight recent signals more heavily (exponential decay)
- Look for divergences between sentiment and price
- Identify sentiment extremes (euphoria = top signal, extreme fear = bottom signal)
- Provide a sentiment score from -100 (extreme fear) to +100 (extreme greed)
- Explain key drivers behind current sentiment"""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        news_sentiments = kwargs.get("news_sentiments", [])
        fear_greed = kwargs.get("fear_greed_index", None)
        social_data = kwargs.get("social_data", {})

        prompt = f"""Analyze market sentiment for {coin_name} ({coin_symbol.upper()}):

## News Sentiment Data
Bullish articles: {news_sentiments.get('bullish', 0)}
Bearish articles: {news_sentiments.get('bearish', 0)}
Neutral articles: {news_sentiments.get('neutral', 0)}

## Fear & Greed Index
{fear_greed or 'Not available'}

## Social Media Indicators
{social_data or 'Not available'}

Provide complete sentiment breakdown with rationale."""

        return prompt

    def get_output_schema(self) -> Type[BaseModel]:
        return SentimentAnalysisOutput
