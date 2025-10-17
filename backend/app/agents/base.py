"""Base class for conversational agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Tuple


class BaseAgent(ABC):
    """Abstract agent that provides a conversation interface."""

    @abstractmethod
    def handle_message(
        self,
        message: str,
        context: Dict[str, object],
        attachments: Iterable[dict],
    ) -> Tuple[str, Dict[str, object]]:
        """Process the user message and return response with updated context."""

