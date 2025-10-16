"""API routes for the AgenticAI backend."""

from fastapi import APIRouter, Depends

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.agent_registry import AgentRegistry, get_agent_registry

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
