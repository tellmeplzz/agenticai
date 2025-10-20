"""Conversation agent specialised for OCR document understanding."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from fastapi.concurrency import run_in_threadpool

from .base import AgentResponse, BaseAgent
from ..services.llm_service import LLMService
from ..services.ocr_service import OCRService
from ..services.prompt_service import PromptService


class OCRConversationAgent(BaseAgent):
    """Agent that combines OCR extraction with LLM reasoning."""

    def __init__(
        self,
        ocr_service: OCRService,
        prompt_service: PromptService,
        llm_service: LLMService,
    ) -> None:
        self._ocr_service = ocr_service
        self._prompt_service = prompt_service
        self._llm_service = llm_service

    async def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[Mapping[str, object]],
    ) -> AgentResponse:
        attachment_payload = list(attachments)
        ocr_results = await run_in_threadpool(
            self._ocr_service.run_ocr, attachment_payload
        )
        combined_context = "\n".join(ocr_results)
        history = self._extract_history(context)
        prompt = self._prompt_service.build_ocr_prompt(
            query=message,
            document_context=combined_context,
            history=history,
        )

        response_text = await self._llm_service.complete(prompt=prompt)

        updated_context = self._build_context(
            context=context,
            user_message=message,
            agent_message=response_text,
            attachments=[att.get("name", "") for att in attachment_payload],
        )
        updated_context.setdefault("ocr_history", []).append(
            {"query": message, "documents": ocr_results}
        )

        return AgentResponse(message=response_text, context=updated_context)

    def _extract_history(self, context: Dict[str, object]) -> List[Dict[str, str]]:
        raw_history = context.get("conversation_history", [])
        if isinstance(raw_history, list):
            entries = []
            for item in raw_history:
                if not isinstance(item, Mapping):
                    continue
                role = str(item.get("role", "")).strip()
                message = str(item.get("message", "")).strip()
                if not role or not message:
                    continue
                entries.append({"role": role, "message": message})
            return entries
        return []

    def _build_context(
        self,
        context: Dict[str, object],
        user_message: str,
        agent_message: str,
        attachments: Iterable[str],
    ) -> Dict[str, object]:
        updated_context = dict(context)
        existing_history = updated_context.get("conversation_history", [])
        if isinstance(existing_history, list):
            history: List[Dict[str, object]] = list(existing_history)
        else:
            history = []
        history.append(
            {
                "role": "user",
                "message": user_message,
                "attachments": [name for name in attachments if name],
            }
        )
        history.append({"role": "agent", "message": agent_message})
        max_entries = 20
        if len(history) > max_entries:
            history = history[-max_entries:]
        updated_context["conversation_history"] = history
        return updated_context
