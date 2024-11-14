
import asyncio
import time
from typing import List

from .defi.core.automation import CoboAutomation
from .defi.core.events import Action, Event


async def my_events():
    """
    Customize your own events here
    """
    while True:
        await asyncio.sleep(1)
        yield Event(type="tick", data={"timestamp": time.time()})


async def my_strategy(event: Event) -> List[Action]:
    """
    Customize your own strategies here
    """
    if event.type == "tick":
        return [Action(type="log", data={"message": "Tick received"})]
    return []


async def my_executor(action: Action):
    """
    Customize your own executors here
    """
    if action.type == "log":
        print(action.data["message"])

# simple example to print a message every second
async def main():
    automation = CoboAutomation()

    # add collectors
    automation.add_collector(my_events)

    # add strategies
    automation.add_strategy(my_strategy)

    # add executors
    automation.add_executor(my_executor)

    # start the automation
    await automation.start()
    # wait for the automation to finish
    await automation.join()
    # stop the automation
    await automation.stop()


if __name__ == "__main__":
    asyncio.run(main())

