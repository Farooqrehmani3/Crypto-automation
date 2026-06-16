"""
OpenAI Client Integration

Provides structured output generation using GPT-4o.
Handles retry logic, token counting, and cost tracking.
"""

import json
import time
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

# GPT-4o pricing per 1M tokens (as of 2025)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


class StructuredOutputError(Exception):
    """Raised when structured output generation fails."""
    pass


class OpenAIService:
    """Async OpenAI service with structured output support."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = "gpt-4o"
        self.fast_model = "gpt-4o-mini"
        self.max_retries = 3

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate API cost based on token usage."""
        pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 6)

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> tuple[T, dict]:
        """Generate structured output using OpenAI's parse mode.

        Returns:
            Tuple of (parsed Pydantic model, metadata dict with tokens/cost)
        """
        model_name = model or self.default_model
        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                response = await self.client.beta.chat.completions.parse(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                parsed = response.choices[0].message.parsed
                if parsed is None:
                    # Try to get the refusal or fallback
                    refusal = response.choices[0].message.refusal
                    if refusal:
                        raise StructuredOutputError(f"Model refused: {refusal}")
                    raise StructuredOutputError("Failed to parse structured output")

                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                cost = self._calculate_cost(model_name, input_tokens, output_tokens)
                elapsed_ms = int((time.time() - start_time) * 1000)

                metadata = {
                    "model": model_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "cost_usd": cost,
                    "processing_time_ms": elapsed_ms,
                    "attempt": attempt + 1,
                }

                logger.info(
                    "Structured output generated",
                    model=model_name,
                    tokens=metadata["total_tokens"],
                    cost=cost,
                    time_ms=elapsed_ms,
                )

                return parsed, metadata

            except RateLimitError:
                wait = 2 ** attempt
                logger.warning(
                    "Rate limited, retrying",
                    attempt=attempt + 1,
                    wait_seconds=wait,
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait)
                else:
                    raise StructuredOutputError("Rate limit exceeded after retries")

            except APITimeoutError:
                logger.error("API timeout", attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    raise StructuredOutputError("API timeout after retries")

            except APIError as e:
                logger.error("API error", error=str(e), attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    raise StructuredOutputError(f"API error: {str(e)}")

        raise StructuredOutputError("Max retries exceeded")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = 0.5,
        max_tokens: int = 2000,
    ) -> tuple[str, dict]:
        """Generate free-form text response."""
        model_name = model or self.default_model
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost = self._calculate_cost(model_name, input_tokens, output_tokens)
            elapsed_ms = int((time.time() - start_time) * 1000)

            metadata = {
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": cost,
                "processing_time_ms": elapsed_ms,
            }

            return text, metadata

        except Exception as e:
            logger.error("Text generation failed", error=str(e))
            raise StructuredOutputError(f"Generation failed: {str(e)}")

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        model: str = None,
        temperature: float = 0.2,
    ) -> tuple[dict, dict]:
        """Generate JSON output using function calling mode (fallback for older models)."""
        model_name = model or self.default_model
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=4000,
            )

            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)

            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost = self._calculate_cost(model_name, input_tokens, output_tokens)
            elapsed_ms = int((time.time() - start_time) * 1000)

            metadata = {
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": cost,
                "processing_time_ms": elapsed_ms,
            }

            return parsed, metadata

        except json.JSONDecodeError as e:
            logger.error("JSON parse error", error=str(e))
            raise StructuredOutputError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error("JSON generation failed", error=str(e))
            raise StructuredOutputError(f"Generation failed: {str(e)}")


# Singleton
openai_service = OpenAIService()
