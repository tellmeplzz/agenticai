"""API routes for the AgenticAI backend."""

from fastapi import APIRouter, Depends

from ..schemas.chat import ChatRequest, ChatResponse
from ..schemas.device_ops import (
    KnowledgeBaseResponse,
    KnowledgeBaseUpsertRequest,
    MaintenanceHistoryResponse,
    MaintenanceRecordCreate,
    MaintenanceRecordResponse,
)
from ..services.agent_registry import AgentRegistry, get_agent_registry
from ..services.agent_registry import get_device_ops_service
from ..services.device_ops_service import DeviceOpsService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    registry: AgentRegistry = Depends(get_agent_registry),
) -> ChatResponse:
    """Dispatch chat requests to the appropriate agent."""

    agent = registry.get_agent(request.agent_id)
    response_text, context_updates = agent.handle_message(
        message=request.message,
        context=request.context or {},
        attachments=request.attachments or [],
    )

    return ChatResponse(
        agent_id=request.agent_id,
        response=response_text,
        context=context_updates,
    )


@router.get(
    "/device-ops/knowledge-base",
    response_model=KnowledgeBaseResponse,
    summary="Retrieve the device operations knowledge base",
)
def get_knowledge_base(
    device_ops_service: DeviceOpsService = Depends(get_device_ops_service),
) -> KnowledgeBaseResponse:
    entries = device_ops_service.get_standard_operating_procedures()
    return KnowledgeBaseResponse(entries=entries)


@router.post(
    "/device-ops/knowledge-base",
    response_model=KnowledgeBaseResponse,
    summary="Create or update a knowledge base article",
)
def upsert_knowledge_base_entry(
    payload: KnowledgeBaseUpsertRequest,
    device_ops_service: DeviceOpsService = Depends(get_device_ops_service),
) -> KnowledgeBaseResponse:
    entries = device_ops_service.upsert_knowledge_article(payload.key, payload.content)
    return KnowledgeBaseResponse(entries=entries)


@router.post(
    "/device-ops/maintenance-records",
    response_model=MaintenanceRecordResponse,
    summary="Record a maintenance activity",
)
def record_maintenance(
    payload: MaintenanceRecordCreate,
    device_ops_service: DeviceOpsService = Depends(get_device_ops_service),
) -> MaintenanceRecordResponse:
    record = device_ops_service.record_maintenance_event(
        device_id=payload.device_id,
        description=payload.description,
        performed_by=payload.performed_by,
        status=payload.status,
        metadata=payload.metadata,
    )
    return MaintenanceRecordResponse(record=record)


@router.get(
    "/device-ops/maintenance-records",
    response_model=MaintenanceHistoryResponse,
    summary="Fetch maintenance history",
)
def list_maintenance_records(
    device_id: str | None = None,
    limit: int | None = None,
    device_ops_service: DeviceOpsService = Depends(get_device_ops_service),
) -> MaintenanceHistoryResponse:
    records = device_ops_service.get_maintenance_history(device_id=device_id, limit=limit)
    return MaintenanceHistoryResponse(records=records)
