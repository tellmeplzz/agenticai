"""Agent that focuses on device operations and maintenance guidance."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from .base import AgentResponse, BaseAgent
from ..services.device_ops_service import DeviceOpsService
from ..services.llm_service import LLMService
from ..services.prompt_service import PromptService


class DeviceOpsAgent(BaseAgent):
    """Agent that synthesizes telemetry insights with knowledge base content."""

    def __init__(
        self,
        device_ops_service: DeviceOpsService,
        prompt_service: PromptService,
        llm_service: LLMService,
    ) -> None:
        self._device_ops_service = device_ops_service
        self._prompt_service = prompt_service
        self._llm_service = llm_service

    async def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[Mapping[str, object]],
    ) -> AgentResponse:
        _ = list(attachments)  # Attachments currently unused but force evaluation.
        telemetry = context.get("telemetry", {})
        summarized = self._device_ops_service.summarize_telemetry(telemetry)
        history = self._extract_history(context)
        prompt = self._prompt_service.build_device_ops_prompt(
            query=message,
            telemetry=summarized,
            history=history,
        )

        response_text = await self._llm_service.complete(prompt=prompt)

        updated_context = self._build_context(
            context=context,
            user_message=message,
            agent_message=response_text,
        )
        updated_context.setdefault("device_ops_history", []).append(
            {"query": message, "telemetry": summarized}
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
    ) -> Dict[str, object]:
        updated_context = dict(context)
        existing_history = updated_context.get("conversation_history", [])
        if isinstance(existing_history, list):
            history: List[Dict[str, object]] = list(existing_history)
        else:
            history = []
        history.append({"role": "user", "message": user_message})
        history.append({"role": "agent", "message": agent_message})
        max_entries = 20
        if len(history) > max_entries:
            history = history[-max_entries:]
        updated_context["conversation_history"] = history
        return updated_context
