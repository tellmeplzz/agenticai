"""Simple LLM client abstraction that can be swapped with real providers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from ..core.config import settings


@dataclass
class LLMService:
    """HTTP client to call the Ollama API or any compatible endpoint."""

    model: str = "llama3"

    async def complete(self, prompt: str, stream: bool = False) -> str:
        payload: Dict[str, object] = {"model": self.model, "prompt": prompt, "stream": stream}
        async with httpx.AsyncClient(base_url=settings.ollama_base_url) as client:
            response = await client.post("/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "response" in data:
                return str(data["response"])
            return json.dumps(data)


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
