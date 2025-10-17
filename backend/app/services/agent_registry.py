"""Agent registry responsible for storing and retrieving agent instances."""

from functools import lru_cache
from typing import Dict

from fastapi import Depends

from ..agents.base import BaseAgent
from ..agents.device_ops_agent import DeviceOpsAgent
from ..agents.ocr_agent import OCRConversationAgent
from ..core.config import settings
from ..services.device_ops_service import DeviceOpsService
from ..services.ocr_service import OCRService
from ..services.prompt_service import PromptService
from ..services.storage_service import StorageService


class AgentRegistry:
    """In-memory registry mapping agent identifiers to instances."""

    def __init__(self, agents: Dict[str, BaseAgent]):
        self._agents = agents

    def get_agent(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents[agent_id]
        except KeyError as exc:  # pragma: no cover - FastAPI handles response
            raise ValueError(f"Unknown agent_id '{agent_id}'") from exc


def build_registry(
    ocr_service: OCRService,
    device_ops_service: DeviceOpsService,
    prompt_service: PromptService,
) -> AgentRegistry:
    """Create the registry with known agents."""

    agents: Dict[str, BaseAgent] = {
        "ocr": OCRConversationAgent(ocr_service=ocr_service, prompt_service=prompt_service),
        "device_ops": DeviceOpsAgent(
            device_ops_service=device_ops_service,
            prompt_service=prompt_service,
        ),
    }
    return AgentRegistry(agents)


# Dependency wiring ---------------------------------------------------------

def get_ocr_service() -> OCRService:
    return OCRService(storage_service=get_storage_service())


def get_device_ops_service() -> DeviceOpsService:
    return DeviceOpsService(storage_service=get_storage_service())


def get_prompt_service() -> PromptService:
    return PromptService()


@lru_cache(maxsize=1)
def get_storage_service() -> StorageService:
    return StorageService(settings.data_dir)


def get_agent_registry(
    ocr_service: OCRService = Depends(get_ocr_service),
    device_ops_service: DeviceOpsService = Depends(get_device_ops_service),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> AgentRegistry:
    return build_registry(
        ocr_service=ocr_service,
        device_ops_service=device_ops_service,
        prompt_service=prompt_service,
    )
