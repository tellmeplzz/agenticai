"""Prompt templating utilities used by multiple agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable


@dataclass
class PromptService:
    """Utility service that assembles prompts for different agent tasks."""

    def build_ocr_prompt(self, query: str, document_context: str) -> str:
        return (
            "You are an OCR assistant. Use the extracted text to answer the user.\n"
            f"OCR context:\n{document_context}\n\n"
            f"User question: {query}\n"
        )

    def build_device_ops_prompt(
        self,
        query: str,
        telemetry: Dict[str, Any],
        knowledge_base: Dict[str, str],
        maintenance_history: Iterable[Dict[str, Any]],
    ) -> str:
        telemetry_lines = "\n".join(f"- {k}: {v}" for k, v in telemetry.items())
        kb_lines = "\n".join(
            f"- {topic}: {detail}" for topic, detail in knowledge_base.items()
        ) or "- 未配置知识库"
        history_lines = "\n".join(
            "- {device_id} | {status} | {description}".format(
                device_id=record.get("device_id", "unknown"),
                status=record.get("status", "unknown"),
                description=record.get("description", ""),
            )
            for record in maintenance_history
        ) or "- 无历史维修记录"
        return (
            "You are a device operations engineer assisting with diagnostics."
            " Combine the telemetry below with standard operating procedures to"
            " craft your response.\n"
            f"Telemetry data:\n{telemetry_lines}\n\n"
            f"Knowledge base:\n{kb_lines}\n\n"
            f"Recent maintenance history:\n{history_lines}\n\n"
            f"User request: {query}\n"
        )
