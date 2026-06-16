"""
Pydantic Output Schemas for all 7 AI Agents

Each agent returns a strictly-typed structured output that OpenAI's
structured output mode enforces. These schemas are used both for
API generation and for database storage (prediction_data JSONB).
"""

from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Agent 1: Technical Analyst
# ============================================================================

class IndicatorReadings(BaseModel):
    rsi: Optional[float] = Field(None, description="RSI (14) value, 0-100")
    macd: Optional[float] = Field(None, description="MACD line value")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    macd_histogram: Optional[float] = Field(None, description="MACD histogram")
    ema_20: Optional[float] = Field(None, description="EMA 20 value")
    ema_50: Optional[float] = Field(None, description="EMA 50 value")
    sma_50: Optional[float] = Field(None, description="SMA 50 value")
    sma_200: Optional[float] = Field(None, description="SMA 200 value")
    bollinger_upper: Optional[float] = Field(None, description="Upper Bollinger Band")
    bollinger_middle: Optional[float] = Field(None, description="Middle Bollinger Band")
    bollinger_lower: Optional[float] = Field(None, description="Lower Bollinger Band")
    atr: Optional[float] = Field(None, description="Average True Range (14)")
    obv: Optional[float] = Field(None, description="On-Balance Volume")


class TechnicalAnalysisOutput(BaseModel):
    signal: str = Field(..., description="Trading signal: bullish, bearish, or neutral")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    indicators: IndicatorReadings
    patterns_detected: list[str] = Field(default_factory=list, description="Detected chart patterns")
    support_levels: list[float] = Field(default_factory=list, description="Key support price levels")
    resistance_levels: list[float] = Field(default_factory=list, description="Key resistance price levels")
    trend: str = Field(..., description="Trend: uptrend, downtrend, or sideways")
    volume_analysis: str = Field(..., description="Volume trend description")
    reasoning: str = Field(..., description="Detailed technical analysis reasoning (2-3 paragraphs)")
    key_observations: list[str] = Field(default_factory=list, description="3-5 key observations")


# ============================================================================
# Agent 2: News Analyst
# ============================================================================

class NewsArticle(BaseModel):
    title: str
    sentiment: str = Field(..., description="bullish, bearish, or neutral")
    confidence: float = Field(..., ge=0, le=1)
    relevance: float = Field(..., ge=0, le=1, description="Relevance to the coin being analyzed")
    key_points: list[str] = Field(default_factory=list)


class NewsAnalysisOutput(BaseModel):
    overall_sentiment: str = Field(..., description="Overall: bullish, bearish, or neutral")
    confidence: float = Field(..., ge=0, le=1)
    articles_analyzed: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    top_articles: list[NewsArticle] = Field(default_factory=list, max_length=5)
    key_themes: list[str] = Field(default_factory=list, description="Recurring themes across articles")
    summary: str = Field(..., description="News summary and impact on the coin")
    reasoning: str = Field(..., description="Detailed reasoning")


# ============================================================================
# Agent 3: Sentiment Analyst
# ============================================================================

class SentimentBreakdown(BaseModel):
    bullish_pct: float = Field(..., ge=0, le=100)
    bearish_pct: float = Field(..., ge=0, le=100)
    neutral_pct: float = Field(..., ge=0, le=100)


class SentimentAnalysisOutput(BaseModel):
    overall_sentiment: str = Field(..., description="bullish, bearish, or neutral")
    sentiment_score: float = Field(..., ge=-100, le=100, description="-100 (extreme fear) to +100 (extreme greed)")
    confidence: float = Field(..., ge=0, le=1)
    breakdown: SentimentBreakdown
    social_media_sentiment: Optional[str] = None
    news_sentiment: Optional[str] = None
    trend_direction: str = Field(..., description="improving, declining, or stable")
    key_drivers: list[str] = Field(default_factory=list, description="Factors driving sentiment")
    reasoning: str = Field(..., description="Sentiment analysis reasoning")


# ============================================================================
# Agent 4: Macro Economic Analyst
# ============================================================================

class MacroEvent(BaseModel):
    event: str
    impact: str = Field(..., description="positive, negative, or neutral for crypto")
    confidence: float = Field(..., ge=0, le=1)
    description: str


class MacroAnalysisOutput(BaseModel):
    overall_impact: str = Field(..., description="positive, negative, or neutral for crypto markets")
    confidence: float = Field(..., ge=0, le=1)
    fed_policy_stance: Optional[str] = Field(None, description="dovish, neutral, or hawkish")
    interest_rate_outlook: Optional[str] = None
    inflation_trend: Optional[str] = None
    regulatory_outlook: Optional[str] = None
    institutional_adoption: Optional[str] = None
    key_events: list[MacroEvent] = Field(default_factory=list)
    crypto_specific_factors: list[str] = Field(default_factory=list)
    summary: str = Field(..., description="Executive summary of macro environment")
    reasoning: str = Field(..., description="Detailed reasoning with economic context")


# ============================================================================
# Agent 5: Forecast Agent
# ============================================================================

class ForecastPoint(BaseModel):
    timestamp: str = Field(..., description="ISO 8601 datetime")
    predicted_price: float
    upper_bound: float
    lower_bound: float


class HorizonForecast(BaseModel):
    predicted_price: float
    predicted_direction: str = Field(..., description="up, down, or sideways")
    confidence: float = Field(..., ge=0, le=1)
    upper_bound: float
    lower_bound: float
    probability_up: float = Field(..., ge=0, le=100)
    probability_down: float = Field(..., ge=0, le=100)
    reasoning: str


class ForecastOutput(BaseModel):
    hour_24: HorizonForecast = Field(alias="24h")
    day_3: HorizonForecast = Field(alias="3d")
    day_7: HorizonForecast = Field(alias="7d")
    day_30: HorizonForecast = Field(alias="30d")
    forecast_series: list[ForecastPoint] = Field(default_factory=list)
    model_confidence: float = Field(..., ge=0, le=1, description="Overall model confidence")
    key_factors: list[str] = Field(default_factory=list, description="Factors driving the forecast")
    risks_to_forecast: list[str] = Field(default_factory=list)
    summary: str = Field(..., description="Forecast executive summary")

    class Config:
        populate_by_name = True


# ============================================================================
# Agent 6: Risk Analyst
# ============================================================================

class RiskMetrics(BaseModel):
    volatility_30d: Optional[float] = Field(None, description="30-day annualized volatility as decimal")
    volatility_90d: Optional[float] = Field(None, description="90-day annualized volatility")
    max_drawdown_30d: Optional[float] = Field(None, description="Maximum drawdown percentage as decimal")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")
    sortino_ratio: Optional[float] = Field(None, description="Sortino ratio")
    var_95: Optional[float] = Field(None, description="Value at Risk (95% confidence)")
    var_99: Optional[float] = Field(None, description="Value at Risk (99% confidence)")
    beta_vs_btc: Optional[float] = Field(None, description="Beta relative to Bitcoin")
    correlation_btc: Optional[float] = Field(None, description="Correlation with Bitcoin (0-1)")


class RiskAnalysisOutput(BaseModel):
    risk_level: str = Field(..., description="low, moderate, high, or extreme")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score 0-100")
    confidence: float = Field(..., ge=0, le=1)
    metrics: RiskMetrics
    risk_factors: list[str] = Field(default_factory=list, description="Key risk factors identified")
    mitigants: list[str] = Field(default_factory=list, description="Risk mitigation suggestions")
    reasoning: str = Field(..., description="Detailed risk analysis reasoning")


# ============================================================================
# Agent 7: Final Report Agent
# ============================================================================

class PriceTarget(BaseModel):
    bullish: float
    base: float
    bearish: float


class FinalReportOutput(BaseModel):
    overall_rating: str = Field(..., description="STRONG_BUY, BUY, HOLD, SELL, or STRONG_SELL")
    rating_score: float = Field(..., ge=0, le=10, description="Numerical rating 0-10")
    confidence: float = Field(..., ge=0, le=1)
    executive_summary: str = Field(..., description="2-3 paragraph executive summary")
    technical_outlook: str
    sentiment_outlook: str
    macro_outlook: str
    forecast_range: str = Field(..., description="e.g. $65,000 - $72,000")
    price_targets: PriceTarget
    key_catalysts: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    recommendation: str = Field(..., description="Detailed investment recommendation")
    time_horizon: str = Field(..., description="Investment time horizon recommendation")
