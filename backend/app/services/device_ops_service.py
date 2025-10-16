"""Device operations service providing telemetry and maintenance utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DeviceOpsService:
    """Facade over device telemetry and maintenance workflows."""

    knowledge_base: Dict[str, str] = field(
        default_factory=lambda: {
            "reset_procedure": "1. Power down the device. 2. Wait 30s. 3. Power up.",
            "firmware_update": "Use the maintenance console with image v2.3.1.",
        }
    )

    def get_standard_operating_procedures(self) -> Dict[str, str]:
        return self.knowledge_base

    def summarize_telemetry(self, telemetry: Dict[str, str]) -> Dict[str, str]:
        summary = {key: value for key, value in telemetry.items() if value}
        summary.update({"reference_procedure": self.knowledge_base.get("reset_procedure", "")})
        return summary
