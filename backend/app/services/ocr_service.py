"""OCR service abstraction used by the OCR agent."""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pdfplumber
from PIL import Image

from ..core.config import settings
from .storage_service import StorageService

LOGGER = logging.getLogger(__name__)


class OCRService:
    """Service responsible for running OCR on provided documents using local engines."""

    SUPPORTED_IMAGE_TYPES: Tuple[str, ...] = (
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "image/bmp",
        "image/tiff",
    )
    SUPPORTED_TYPES: Tuple[str, ...] = SUPPORTED_IMAGE_TYPES + ("application/pdf",)

    def __init__(self, storage_service: StorageService, resolution: int = 300) -> None:
        self.resolution = resolution
        self._storage_service = storage_service
        self._engine = None
        self._recent_artifacts: List[Dict[str, str]] = []

    def run_ocr(self, attachments: Iterable[dict]) -> List[str]:
        """Run OCR on attachments via the configured local engine, returning extracted text."""

        texts: List[str] = []
        self._recent_artifacts = []
        for attachment in attachments:
            content_type = (attachment.get("content_type") or "").lower()
            if content_type not in self.SUPPORTED_TYPES:
                LOGGER.debug("Skipping unsupported attachment type: %s", content_type)
                continue

            payload = self._load_attachment_payload(attachment)
            if payload is None:
                LOGGER.warning("Attachment missing usable data: %s", attachment)
                continue

            if content_type == "application/pdf":
                extracted = self._extract_from_pdf(payload)
            else:
                extracted = self._extract_from_image_bytes(payload)

            if not extracted:
                continue

            texts.extend(extracted)

            combined_text = "\n".join(extracted)
            attachment_name = (
                attachment.get("name")
                or attachment.get("filename")
                or attachment.get("path")
                or "attachment"
            )
            metadata = {
                "attachment_name": attachment_name,
                "content_type": content_type,
            }
            artifact = self._storage_service.persist_ocr_document(
                attachment_name,
                combined_text,
                metadata=metadata,
                source_bytes=payload,
            )
            artifact.update({"attachment_name": attachment_name})
            self._recent_artifacts.append(artifact)

        return [text for text in texts if text]

    def get_recent_artifacts(self) -> List[Dict[str, str]]:
        """Return metadata about the most recent OCR persistence operations."""

        return list(self._recent_artifacts)

    def _extract_from_pdf(self, data: bytes) -> List[str]:
        results: List[str] = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    image = page.to_image(resolution=self.resolution).original
                except Exception as exc:  # pragma: no cover - defensive
                    LOGGER.warning("Failed to rasterize page %s: %s", page_number, exc)
                    continue
                results.extend(self._extract_from_image(image, source=f"page {page_number}"))
        return results

    def _extract_from_image_bytes(self, data: bytes) -> List[str]:
        try:
            image = Image.open(io.BytesIO(data))
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("Failed to open image bytes: %s", exc)
            return []
        return self._extract_from_image(image)

    def _extract_from_image(self, image: Image.Image, *, source: str | None = None) -> List[str]:
        engine = self._get_engine()
        image = image.convert("RGB")
        np_image = np.array(image)
        try:
            ocr_result = engine.ocr(np_image, cls=False)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.error("OCR engine failed on %s: %s", source or "image", exc)
            return []

        return self._parse_ocr_result(ocr_result)

    def _get_engine(self):
        if self._engine is not None:
            return self._engine

        provider = settings.ocr_provider.lower()
        if provider != "paddleocr":
            raise RuntimeError(
                f"Unsupported OCR provider '{settings.ocr_provider}'. Currently only 'paddleocr' is available."
            )

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:  # pragma: no cover - import guarded
            raise RuntimeError(
                "PaddleOCR is not installed. Install it with 'pip install paddleocr'."
            ) from exc

        self._engine = PaddleOCR(
            use_angle_cls=True,
            lang=settings.ocr_lang,
            show_log=False,
            use_gpu=bool(settings.ocr_use_gpu),
        )
        return self._engine

    @staticmethod
    def _parse_ocr_result(result: Sequence) -> List[str]:
        texts: List[str] = []
        if not isinstance(result, Sequence):
            return texts

        for entry in result:
            if isinstance(entry, Sequence):
                # paddleocr may nest results per image -> list[list[tuple]]
                for candidate in entry:
                    text = OCRService._extract_text_from_candidate(candidate)
                    if text:
                        texts.append(text)
            else:
                text = OCRService._extract_text_from_candidate(entry)
                if text:
                    texts.append(text)
        return texts

    @staticmethod
    def _extract_text_from_candidate(candidate: object) -> Optional[str]:
        if not isinstance(candidate, Sequence) or len(candidate) < 2:
            return None
        metadata = candidate[1]
        if not isinstance(metadata, Sequence) or not metadata:
            return None
        text = metadata[0]
        if isinstance(text, str):
            text = text.strip()
        return text or None

    @staticmethod
    def _load_attachment_payload(attachment: dict) -> Optional[bytes]:
        data = attachment.get("data")
        if data:
            try:
                return base64.b64decode(data)
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Failed to decode attachment data: %s", exc)
                return None

        path_value = attachment.get("path")
        if path_value:
            try:
                return Path(path_value).read_bytes()
            except FileNotFoundError:
                LOGGER.warning("Attachment path not found: %s", path_value)
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Failed to read attachment path %s: %s", path_value, exc)
        return None
