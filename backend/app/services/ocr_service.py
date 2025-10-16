"""OCR service abstraction used by the OCR agent."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Iterable, List, Tuple


class OCRService:
    """Service responsible for running OCR on provided documents."""

    SUPPORTED_TYPES: Tuple[str, ...] = (
        "image/png",
        "image/jpeg",
        "application/pdf",
    )

    def run_ocr(self, attachments: Iterable[dict]) -> List[str]:
        """Run OCR on attachments, returning extracted text segments."""

        texts: List[str] = []
        for attachment in attachments:
            content_type = attachment.get("content_type")
            if content_type not in self.SUPPORTED_TYPES:
                continue

            data = attachment.get("data")
            if data:
                decoded = base64.b64decode(data)
                texts.append(self._fake_ocr(decoded, content_type))
            else:
                path = attachment.get("path")
                if path:
                    texts.append(self._fake_ocr(Path(path).read_bytes(), content_type))
        return texts

    @staticmethod
    def _fake_ocr(_: bytes, content_type: str) -> str:
        """Placeholder OCR implementation to be replaced with a real engine."""

        return f"[Simulated OCR output from {content_type}]"
