import uuid
from automation.defi.core.automation import CoboAutomation
from automation.defi.core.events import Action, Event
import asyncio
from web3 import AsyncHTTPProvider, AsyncWeb3
import cobo_waas2

from typing import List

from automation.defi.executors.devapi import DevApiExecutor, DevApiTransactionAction


"""
Suppose we have an MPC wallet in Portal that has ETH assets doing yield farming in the
Stargate protocol on Base chain. We want to create a harvesting bot that executes once
reward is greater than a threshold.

For this automation task, we would need to:
1. Monitor the reward balance in Stargate protocol
2. Create a strategy to check if it's time to harvest (reward is greater than a threshold)
3. Execute the harvest transaction through Cobo WaaS API
"""

wallet_address = "<wallet_address>"
wallet_id = "<wallet_id>"
api_private_key = "<api_private_key>"
threshold = 1 * 10**18
rpc_url = "<rpc_url>"
staking_lp_address = "<staking_lp_address>"
stargate_multi_rewarder_address = "0x9Aa02D4Fae7F58b8E8f34c66E756cC734DAc7fe4"
stargate_staking_address = "0xDFc47DCeF7e8f9Ab19a1b8Af3eeCF000C7ea0B80"


async def get_stg_reward(w3: AsyncWeb3):
    stargate_multi_rewarder = w3.eth.contract(
        address=stargate_multi_rewarder_address,
        abi=[
            {
                "inputs": [
                    {
                        "internalType": "contract IERC20",
                        "name": "stakingToken",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "user", "type": "address"},
                ],
                "name": "getRewards",
                "outputs": [
                    {"internalType": "address[]", "name": "", "type": "address[]"},
                    {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
                ],
                "stateMutability": "view",
                "type": "function",
            }
        ],
    )
    rewards = await stargate_multi_rewarder.functions.getRewards(
        staking_lp_address, wallet_address
    ).call()
    return rewards[1][0]


async def collect_reward_events():
    """
    Monitor stargate rewards for a wallet
    """
    w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
    while True:
        await asyncio.sleep(1)
        yield Event(type="reward", data={"amount": await get_stg_reward(w3)})


async def build_claim_reward_request(amount: int):
    stargate_staking = AsyncWeb3().eth.contract(
        address=stargate_staking_address,
        abi=[
            {
                "inputs": [
                    {
                        "internalType": "contract IERC20[]",
                        "name": "lpTokens",
                        "type": "address[]",
                    },
                ],
                "name": "claim",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ],
    )
    calldata = stargate_staking.encode_abi("claim", [[staking_lp_address]])
    return cobo_waas2.ContractCallParams(
        request_id=str(uuid.uuid4()),
        chain_id="BASE_ETH",
        source=cobo_waas2.ContractCallSource(
            actual_instance=cobo_waas2.MpcContractCallSource(
                wallet_id=wallet_id,
                address=wallet_address,
                source_type=cobo_waas2.ContractCallSourceType.USER_CONTROLLED,
            )
        ),
        destination=cobo_waas2.ContractCallDestination(
            actual_instance=cobo_waas2.EvmContractCallDestination(
                destination_type=cobo_waas2.ContractCallDestinationType.EVM_CONTRACT,
                address=stargate_multi_rewarder_address,
                calldata=calldata,
            )
        ),
    )


async def claim_reward_strategy(event: Event) -> List[Action]:
    """
    Claim reward strategy, claim reward when reward is greater than a threshold
    """
    if event.type == "reward":
        if event.data["amount"] >= threshold:
            request = await build_claim_reward_request(event.data["amount"])
            return [DevApiTransactionAction(data=request.model_dump())]
    return []


async def main():
    automation = CoboAutomation()

    # collect rewards
    automation.add_collector(collect_reward_events)

    # add strategies
    automation.add_strategy(claim_reward_strategy)

    # use devapi to claim rewards
    automation.add_executor(DevApiExecutor(api_private_key, "development"))

    # start the automation
    await automation.start()
    # wait for the automation to finish
    await automation.join()
    # stop the automation
    await automation.stop()


if __name__ == "__main__":
    asyncio.run(main())
