"""
Final Report Agent — Synthesizes all agent outputs into an executive summary.
"""

from typing import Type
from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.agents.schemas import FinalReportOutput


class ReportAgent(BaseAgent):
    """Agent 7: Final Report Synthesis Expert"""

    def __init__(self):
        super().__init__(
            name="Report Agent",
            description="Senior analyst synthesizing all agent outputs into an executive summary with actionable recommendation",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=3000,
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Chief Investment Strategist for a crypto hedge fund. You synthesize outputs from 6 specialized agents into a comprehensive final report.

Rating scale:
- STRONG_BUY (8-10): Multiple agents bullish, high confidence, strong catalysts
- BUY (6-8): Generally bullish with some concerns
- HOLD (4-6): Mixed signals, wait for clarity
- SELL (2-4): Generally bearish, deteriorating conditions
- STRONG_SELL (0-2): Multiple agents bearish, high risk, exit position

Your report must:
1. Weigh each agent's signal by their confidence level
2. Identify consensus vs conflicting signals
3. Highlight key catalysts and risks
4. Provide specific price targets (bullish/base/bearish)
5. Give clear, actionable recommendation with time horizon
6. Be balanced — acknowledge uncertainty where present
7. Mention position sizing relative to risk (never risk more than 1-5% per trade)"""

    def build_user_prompt(self, **kwargs) -> str:
        coin_name = kwargs.get("coin_name", "Unknown")
        coin_symbol = kwargs.get("symbol", "UNKNOWN")
        current_price = kwargs.get("current_price", 0)
        agent_outputs = kwargs.get("agent_outputs", {})

        agents_summary = ""
        for agent_name, output in agent_outputs.items():
            agents_summary += f"\n### {agent_name}\n{output}\n"

        return f"""Synthesize final report for {coin_name} ({coin_symbol.upper()}) at ${current_price:,.2f}:

{agents_summary}

Generate a comprehensive executive report with:
1. Overall rating and score (0-10)
2. Executive summary (2-3 paragraphs)
3. Price targets (bullish, base, bearish)
4. Key catalysts and risks
5. Clear investment recommendation with time horizon"""

    def get_output_schema(self) -> Type[BaseModel]:
        return FinalReportOutput
