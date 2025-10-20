"""API routes for the AgenticAI backend."""

from fastapi import APIRouter, Depends

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.agent_registry import AgentRegistry, get_agent_registry

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    registry: AgentRegistry = Depends(get_agent_registry),
) -> ChatResponse:
    """Dispatch chat requests to the appropriate agent."""

    agent = registry.get_agent(request.agent_id)
    agent_response = await agent.handle_message(
        message=request.message,
        context=request.context or {},
        attachments=[attachment.dict() for attachment in request.attachments or []],
    )

    return ChatResponse(
        agent_id=request.agent_id,
        response=agent_response.message,
        context=agent_response.context,
    )
