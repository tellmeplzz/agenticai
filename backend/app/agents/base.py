"""Base types shared by all conversational agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping


@dataclass
class AgentResponse:
    """Normalized response returned by every agent."""

    message: str
    context: Dict[str, object]


class BaseAgent(ABC):
    """Abstract conversation agent interface."""

    @abstractmethod
    async def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[Mapping[str, object]],
    ) -> AgentResponse:
        """Process the user message and return the model response and new context."""

