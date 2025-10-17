"""Pydantic schemas for device operations APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class KnowledgeBaseUpsertRequest(BaseModel):
    key: str = Field(..., description="Knowledge base topic identifier")
    content: str = Field(..., description="Content for the knowledge base entry")


class KnowledgeBaseResponse(BaseModel):
    entries: Dict[str, str]


class MaintenanceRecordCreate(BaseModel):
    device_id: str = Field(..., description="Target device identifier")
    description: str = Field(..., description="Summary of the maintenance action")
    performed_by: Optional[str] = Field(None, description="Engineer or operator name")
    status: Optional[str] = Field(None, description="Status of the maintenance action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class MaintenanceRecord(BaseModel):
    device_id: str
    description: str
    performed_by: Optional[str] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    recorded_at: str


class MaintenanceHistoryResponse(BaseModel):
    records: List[MaintenanceRecord]


class MaintenanceRecordResponse(BaseModel):
    record: MaintenanceRecord
