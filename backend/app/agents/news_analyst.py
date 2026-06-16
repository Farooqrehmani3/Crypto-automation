"""
News Analyst Agent — Analyzes crypto news articles and classifies sentiment.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import NewsAnalysisOutput


class NewsAnalystAgent(BaseAgent):
    """Agent 2: News Analysis Expert"""

    def __init__(self):
        super().__init__(
            name="News Analyst",
            description="Crypto news analyst that classifies articles and assesses market impact",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=2500,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a senior cryptocurrency news analyst. Your expertise:
- Analyze news articles for cryptocurrency market impact
- Classify each article as BULLISH (positive for price), BEARISH (negative), or NEUTRAL
- Identify key themes and narratives driving markets
- Assess relevance of news to specific coins
- Consider source credibility and potential market reaction

Classification guidelines:
- BULLISH: Positive adoption news, ETF approvals, institutional investment, favorable regulation, major partnerships, successful upgrades
- BEARISH: Hacks, scams, regulatory crackdowns, exchange failures, negative macro news, protocol vulnerabilities
- NEUTRAL: Technical updates without price impact, routine announcements, industry reports

Output detailed analysis with per-article classification and overall thesis."""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        articles = kwargs.get("articles", [])

        articles_text = ""
        for i, article in enumerate(articles[:50]):
            articles_text += f"""
### Article {i+1}
**Title:** {article.get('title', 'N/A')}
**Source:** {article.get('source', 'Unknown')}
**Published:** {article.get('published_at', 'Unknown')}
**Content:** {article.get('content', article.get('summary', 'No content available'))[:500]}
---
"""

        return f"""Analyze news for {coin_name} ({coin_symbol.upper()}):

{articles_text}

Provide:
1. Overall sentiment assessment (bullish/bearish/neutral)
2. Classification of each article with confidence scores
3. Key themes across articles
4. Summary of how news impacts {coin_symbol.upper()}"""

    def get_output_schema(self) -> Type[BaseModel]:
        return NewsAnalysisOutput
