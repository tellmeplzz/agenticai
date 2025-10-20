"""Prompt templating utilities used by multiple agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping


@dataclass
class PromptService:
    """Utility service that assembles prompts for different agent tasks."""

    def _format_history(self, history: Iterable[Mapping[str, str]]) -> str:
        """Render a readable chat history block for inclusion in prompts."""

        lines = []
        for entry in history:
            role = entry.get("role", "user").title()
            message = entry.get("message", "")
            if not message:
                continue
            lines.append(f"{role}: {message}")
        if not lines:
            return "No prior conversation."
        return "\n".join(lines)

    def build_ocr_prompt(
        self,
        query: str,
        document_context: str,
        history: Iterable[Mapping[str, str]] | None = None,
    ) -> str:
        history_block = self._format_history(history or [])
        return (
            "You are an OCR assistant. Use the extracted text to answer the user.\n"
            f"Conversation so far:\n{history_block}\n\n"
            f"OCR context:\n{document_context}\n\n"
            f"User question: {query}\n"
        )

    def build_device_ops_prompt(
        self,
        query: str,
        telemetry: Dict[str, str],
        history: Iterable[Mapping[str, str]] | None = None,
    ) -> str:
        if telemetry:
            telemetry_lines = "\n".join(f"- {k}: {v}" for k, v in telemetry.items())
        else:
            telemetry_lines = "- No telemetry supplied"
        history_block = self._format_history(history or [])
        return (
            "You are a device operations engineer assisting with diagnostics."
            " Combine the telemetry below with standard operating procedures to"
            " craft your response.\n"
            f"Conversation so far:\n{history_block}\n\n"
            f"Telemetry data:\n{telemetry_lines}\n\n"
            f"User request: {query}\n"
        )
