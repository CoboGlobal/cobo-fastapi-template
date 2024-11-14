from abc import ABC, abstractmethod
from typing import AsyncIterable, List, Callable, Awaitable
from .events import Event, Action


class Collector(ABC):
    @abstractmethod
    async def start(self) -> "Collector":
        """Start the collector."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the collector."""
        pass

    @abstractmethod
    async def events(self) -> AsyncIterable[Event]:
        """Continuously yield events."""
        pass

class Strategy(ABC):
    @abstractmethod
    async def process_event(self, event: Event) -> List[Action]:
        """Process an event and return a list of actions."""
        pass

class Executor(ABC):
    @abstractmethod
    async def execute(self, action: Action):
        """Execute an action."""
        pass


class FunctionCollector(Collector):
    def __init__(self, events_func: Callable[[], AsyncIterable[Event]]):
        self.events_func = events_func
        
    async def start(self) -> "Collector":
        return self
        
    async def stop(self):
        pass
        
    async def events(self) -> AsyncIterable[Event]:
        async for event in self.events_func():
            yield event

class FunctionStrategy(Strategy):
    def __init__(self, process_func: Callable[[Event], Awaitable[List[Action]]]):
        self.process_func = process_func
        
    async def process_event(self, event: Event) -> List[Action]:
        return await self.process_func(event)

class FunctionExecutor(Executor):
    def __init__(self, execute_func: Callable[[Action], Awaitable[None]]):
        self.execute_func = execute_func
        
    async def execute(self, action: Action):
        await self.execute_func(action)