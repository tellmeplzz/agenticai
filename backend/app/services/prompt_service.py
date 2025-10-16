"""Prompt templating utilities used by multiple agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PromptService:
    """Utility service that assembles prompts for different agent tasks."""

    def build_ocr_prompt(self, query: str, document_context: str) -> str:
        return (
            "You are an OCR assistant. Use the extracted text to answer the user.\n"
            f"OCR context:\n{document_context}\n\n"
            f"User question: {query}\n"
        )

    def build_device_ops_prompt(self, query: str, telemetry: Dict[str, str]) -> str:
        telemetry_lines = "\n".join(f"- {k}: {v}" for k, v in telemetry.items())
        return (
            "You are a device operations engineer assisting with diagnostics."
            " Combine the telemetry below with standard operating procedures to"
            " craft your response.\n"
            f"Telemetry data:\n{telemetry_lines}\n\n"
            f"User request: {query}\n"
        )
