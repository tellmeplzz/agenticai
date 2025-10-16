"""Agent that focuses on device operations and maintenance guidance."""

from __future__ import annotations

import asyncio
from typing import Dict, Iterable, Tuple

from .base import BaseAgent
from ..services.device_ops_service import DeviceOpsService
from ..services.llm_service import get_llm_service
from ..services.prompt_service import PromptService


class DeviceOpsAgent(BaseAgent):
    """Agent that synthesizes telemetry insights with knowledge base content."""

    def __init__(self, device_ops_service: DeviceOpsService, prompt_service: PromptService):
        self._device_ops_service = device_ops_service
        self._prompt_service = prompt_service

    def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[dict],
    ) -> Tuple[str, Dict[str, object]]:
        telemetry = context.get("telemetry", {})
        summarized = self._device_ops_service.summarize_telemetry(telemetry)
        prompt = self._prompt_service.build_device_ops_prompt(message, summarized)

        response_text = asyncio.run(get_llm_service().complete(prompt=prompt))

        updated_context = dict(context)
        updated_context.setdefault("device_ops_history", []).append(
            {"query": message, "telemetry": summarized}
        )

        return response_text, updated_context
