"""Pydantic schemas for chat endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """Attachment metadata for uploaded files."""

    name: str = Field(..., description="Filename or logical name of the attachment")
    content_type: Optional[str] = Field(
        None, description="MIME type to guide processing"
    )
    data: Optional[str] = Field(
        None,
        description=(
            "Base64 encoded payload for lightweight uploads. Larger files should be"
            " handled via presigned URLs or a dedicated storage service."
        ),
    )


class ChatRequest(BaseModel):
    """Request schema for chat interactions with agents."""

    agent_id: str = Field(..., description="Identifier of the target agent")
    message: str = Field(..., description="User message or instruction")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Conversation state maintained by the client",
    )
    attachments: Optional[List[Attachment]] = Field(
        default=None,
        description="Optional attachments such as documents or images",
    )


class ChatResponse(BaseModel):
    """Response schema for agent outputs."""

    agent_id: str
    response: str
    context: Dict[str, Any] = Field(default_factory=dict)
