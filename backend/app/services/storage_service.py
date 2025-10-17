"""Persistent storage utilities for agent data."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageService:
    """Provide simple JSON and file-based persistence for agents."""

    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._knowledge_base_path = self.root / "knowledge_base.json"
        self._maintenance_path = self.root / "maintenance_records.jsonl"
        self._ocr_dir = self.root / "ocr_results"
        self._ocr_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Knowledge base helpers
    # ------------------------------------------------------------------
    def ensure_knowledge_base_defaults(self, defaults: Dict[str, str]) -> Dict[str, str]:
        """Ensure default knowledge base entries exist on disk."""

        current = self.load_knowledge_base()
        updated = False
        for key, value in defaults.items():
            if key not in current:
                current[key] = value
                updated = True
        if updated:
            self.save_knowledge_base(current)
        return current

    def load_knowledge_base(self) -> Dict[str, str]:
        if not self._knowledge_base_path.exists():
            return {}
        try:
            data = json.loads(self._knowledge_base_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return {str(key): str(value) for key, value in data.items()}

    def save_knowledge_base(self, entries: Dict[str, str]) -> None:
        payload = {str(key): str(value) for key, value in entries.items()}
        self._knowledge_base_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def upsert_knowledge_article(self, key: str, content: str) -> Dict[str, str]:
        entries = self.load_knowledge_base()
        entries[key] = content
        self.save_knowledge_base(entries)
        return entries

    # ------------------------------------------------------------------
    # Maintenance records helpers
    # ------------------------------------------------------------------
    def load_maintenance_records(self) -> List[Dict[str, Any]]:
        if not self._maintenance_path.exists():
            return []
        records: List[Dict[str, Any]] = []
        for line in self._maintenance_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def append_maintenance_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(record)
        record.setdefault("recorded_at", datetime.utcnow().isoformat())
        with self._maintenance_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    # ------------------------------------------------------------------
    # OCR result storage helpers
    # ------------------------------------------------------------------
    def persist_ocr_document(
        self,
        base_name: Optional[str],
        content: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        source_bytes: Optional[bytes] = None,
    ) -> Dict[str, str]:
        """Store OCR text and optional metadata to disk."""

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
        safe_stem = self._sanitize_stem(base_name) or "ocr_document"
        file_path = self._ocr_dir / f"{safe_stem}_{timestamp}.txt"
        file_path.write_text(content, encoding="utf-8")

        meta: Dict[str, Any] = {"stored_at": timestamp, "content_path": str(file_path)}
        if metadata:
            meta.update(metadata)
        if source_bytes is not None:
            source_path = self._ocr_dir / f"{safe_stem}_{timestamp}.bin"
            source_path.write_bytes(source_bytes)
            meta["source_path"] = str(source_path)

        meta_path = self._ocr_dir / f"{safe_stem}_{timestamp}.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        result = {"text_path": str(file_path), "metadata_path": str(meta_path)}
        if "source_path" in meta:
            result["source_path"] = meta["source_path"]
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _sanitize_stem(value: Optional[str]) -> str:
        if not value:
            return ""
        stem = "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})
        return stem.strip("-_")
