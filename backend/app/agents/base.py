"""
Base Agent class for AI-powered analysis agents.

Provides structured output generation, cost tracking,
retry logic, and common utilities used by all 7 agents.
"""

import time
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional

from pydantic import BaseModel
from structlog import get_logger

from app.integrations.openai_client import OpenAIService, StructuredOutputError

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """Abstract base class for all AI analysis agents."""

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ):
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.openai = OpenAIService()

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The system prompt that defines this agent's role and expertise."""
        pass

    @abstractmethod
    def build_user_prompt(self, **kwargs) -> str:
        """Build the user prompt with data for analysis."""
        pass

    @abstractmethod
    def get_output_schema(self) -> Type[BaseModel]:
        """Return the Pydantic model for structured output."""
        pass

    async def analyze(self, **kwargs) -> tuple[BaseModel, dict]:
        """Run the agent's analysis.

        Args:
            **kwargs: Data passed to build_user_prompt()

        Returns:
            Tuple of (parsed output model, metadata dict)
        """
        start_time = time.time()
        logger.info(f"Agent started: {self.name}", agent=self.name)

        try:
            user_prompt = self.build_user_prompt(**kwargs)
            output_schema = self.get_output_schema()

            result, metadata = await self.openai.generate_structured(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_model=output_schema,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            elapsed = int((time.time() - start_time) * 1000)
            metadata["agent"] = self.name
            metadata["total_time_ms"] = elapsed

            logger.info(
                f"Agent completed: {self.name}",
                agent=self.name,
                tokens=metadata.get("total_tokens", 0),
                cost=metadata.get("cost_usd", 0),
                time_ms=elapsed,
            )

            return result, metadata

        except StructuredOutputError as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(
                f"Agent failed: {self.name}",
                agent=self.name,
                error=str(e),
                time_ms=elapsed,
            )
            raise

    def get_cost_estimate(self, prompt_length: int) -> float:
        """Estimate API cost for a given prompt length."""
        # Rough estimate: ~2.5x prompt length for response
        total_estimate = prompt_length * 3.5
        return round((total_estimate / 1_000_000) * 12.50, 6)  # $12.50/M tokens

    def format_currency(self, value: float) -> str:
        """Format a number as USD currency."""
        if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        elif value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        else:
            return f"${value:,.2f}"

    def format_percentage(self, value: float) -> str:
        """Format a decimal as percentage string."""
        return f"{value:+.2f}%"
