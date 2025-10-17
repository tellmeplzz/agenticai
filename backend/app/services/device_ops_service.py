"""Device operations service providing telemetry and maintenance utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .storage_service import StorageService


@dataclass
class DeviceOpsService:
    """Facade over device telemetry and maintenance workflows."""

    storage_service: StorageService
    default_knowledge_base: Dict[str, str] = field(
        default_factory=lambda: {
            "reset_procedure": "1. Power down the device. 2. Wait 30s. 3. Power up.",
            "firmware_update": "Use the maintenance console with image v2.3.1.",
        }
    )

    def __post_init__(self) -> None:
        self.storage_service.ensure_knowledge_base_defaults(self.default_knowledge_base)

    def get_standard_operating_procedures(self) -> Dict[str, str]:
        return self.storage_service.load_knowledge_base() or dict(self.default_knowledge_base)

    def upsert_knowledge_article(self, key: str, content: str) -> Dict[str, str]:
        return self.storage_service.upsert_knowledge_article(key, content)

    def summarize_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = telemetry if isinstance(telemetry, dict) else {}
        summary = {key: value for key, value in telemetry.items() if value is not None}
        sop = self.get_standard_operating_procedures()
        if sop:
            summary.setdefault("reference_procedure", sop.get("reset_procedure", ""))
        return summary

    def record_maintenance_event(
        self,
        *,
        device_id: str,
        description: str,
        performed_by: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "device_id": device_id,
            "description": description,
            "performed_by": performed_by,
            "status": status or "pending",
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        return self.storage_service.append_maintenance_record(record)

    def get_maintenance_history(
        self,
        *,
        device_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        records = self.storage_service.load_maintenance_records()
        if device_id:
            records = [record for record in records if record.get("device_id") == device_id]
        records.sort(key=lambda item: item.get("recorded_at", ""), reverse=True)
        if limit is not None:
            records = records[:limit]
        return records
