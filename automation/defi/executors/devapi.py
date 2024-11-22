import logging
import uuid

from pydantic import BaseModel, Field
from ..core.base import Executor
from ..core.events import Action
from services.cobo_service import CoboService


logger = logging.getLogger(__name__)


class DevApiTransactionAction(Action):
    type: str = "devapi_transaction"


class DevApiExecutor(Executor):
    def __init__(self, api_private_key: str, env: str):
        self.api_private_key = api_private_key
        self.env = env
        self.cobo_service = CoboService.get_instance(self.api_private_key, self.env)

    async def execute(self, action: Action):
        logger.info(f"Executing action: {action}")
        if isinstance(action, DevApiTransactionAction):
            await self.cobo_service.create_contract_call_transaction(action.data)
