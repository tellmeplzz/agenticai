"""OCR service abstraction used by the OCR agent."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Iterable, List, Mapping, Tuple


class OCRService:
    """Service responsible for running OCR on provided documents."""

    SUPPORTED_TYPES: Tuple[str, ...] = (
        "image/png",
        "image/jpeg",
        "application/pdf",
    )

    def run_ocr(self, attachments: Iterable[Mapping[str, object]]) -> List[str]:
        """Run OCR on attachments, returning extracted text segments."""

        texts: List[str] = []
        attachments_list = list(attachments)
        for attachment in attachments_list:
            content_type = str(attachment.get("content_type")) if attachment.get("content_type") else None
            if content_type not in self.SUPPORTED_TYPES:
                continue

            data = attachment.get("data")
            if isinstance(data, str) and data:
                decoded = base64.b64decode(data)
                texts.append(self._fake_ocr(decoded, content_type))
                continue

            path = attachment.get("path")
            if isinstance(path, (str, Path)):
                texts.append(self._fake_ocr(Path(path).read_bytes(), content_type))

        if not texts:
            if attachments_list:
                texts.append("[Attachments were provided but none were OCR-compatible]")
            else:
                texts.append("[No attachments provided]")

        return texts

    @staticmethod
    def _fake_ocr(_: bytes, content_type: str) -> str:
        """Placeholder OCR implementation to be replaced with a real engine."""

        return f"[Simulated OCR output from {content_type}]"
