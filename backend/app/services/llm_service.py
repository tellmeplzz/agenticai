"""Simple LLM client abstraction that can be swapped with real providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import httpx

from ..core.config import settings


class LLMServiceError(RuntimeError):
    """Raised when the remote LLM provider returns an unexpected response."""


@dataclass
class LLMService:
    """HTTP client to call the Ollama API or any compatible endpoint."""

    model: str = "llama3"
    timeout: float = 60.0
    _client: httpx.AsyncClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=settings.ollama_base_url, timeout=self.timeout)

    async def complete(self, prompt: str, stream: bool = False) -> str:
        payload: Dict[str, object] = {"model": self.model, "prompt": prompt, "stream": stream}
        response = await self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "response" in data:
            return str(data["response"])
        if isinstance(data, dict):
            raise LLMServiceError("Response payload missing 'response' field")
        return str(data)

    async def aclose(self) -> None:
        await self._client.aclose()


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


async def shutdown_llm_service() -> None:
    global _llm_service
    if _llm_service is not None:
        await _llm_service.aclose()
        _llm_service = None
