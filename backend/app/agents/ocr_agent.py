"""Conversation agent specialised for OCR document understanding."""

from __future__ import annotations

import asyncio
from typing import Dict, Iterable, Tuple

from .base import BaseAgent
from ..services.llm_service import get_llm_service
from ..services.ocr_service import OCRService
from ..services.prompt_service import PromptService


class OCRConversationAgent(BaseAgent):
    """Agent that combines OCR extraction with LLM reasoning."""

    def __init__(self, ocr_service: OCRService, prompt_service: PromptService):
        self._ocr_service = ocr_service
        self._prompt_service = prompt_service

    def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[dict],
    ) -> Tuple[str, Dict[str, object]]:
        ocr_results = self._ocr_service.run_ocr(attachments)
        artifacts = self._ocr_service.get_recent_artifacts()
        combined_context = "\n".join(ocr_results)
        prompt = self._prompt_service.build_ocr_prompt(message, combined_context)

        response_text = asyncio.run(get_llm_service().complete(prompt=prompt))

        updated_context = dict(context)
        updated_context.setdefault("ocr_history", []).append(
            {"query": message, "documents": ocr_results, "artifacts": artifacts}
        )
        if artifacts:
            updated_context.setdefault("ocr_artifacts", artifacts)

        return response_text, updated_context
