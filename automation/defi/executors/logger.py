
import logging
from ..core.base import Executor
from ..core.events import Action

logger = logging.getLogger(__name__)

class LoggerExecutor(Executor):
    async def execute(self, action: Action):
        logger.info(f"Executing action: {action}")