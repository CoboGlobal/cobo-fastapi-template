import logging
from typing import Optional, List, Dict, Any

import cobo_waas2
from cobo_waas2.api import WalletsApi, TransactionsApi
from cobo_waas2.exceptions import ApiException
from cobo_waas2.models import WalletType, WalletSubtype

logger = logging.getLogger(__name__)


class CoboService:
    _instance = None

    @classmethod
    def get_instance(cls, api_private_key: str, env: str):
        if cls._instance is None:
            cls._instance = cls(api_private_key, env)
        return cls._instance

    def __init__(self, api_private_key: str, env: str):
        if CoboService._instance is not None:
            raise Exception(
                "This class is a singleton. Use get_instance() to get the instance."
            )
        self.configuration = cobo_waas2.Configuration(
            # %if auth not in [user]
            api_private_key=api_private_key,
            # %elif auth == org
            # access_token=api_private_key,
            # %endif
            host="https://api.sandbox.cobo.com/v2"
            if env == "sandbox"
            else "https://api.dev.cobo.com/v2"
            if env == "dev"
            else "https://api.cobo.com/v2",
        )
        print(
            f"env={env}, Connecting to Cobo WaaS service at host: {self.configuration.host}"
        )
        CoboService._instance = self

    async def list_wallets(
        self,
        wallet_type: Optional[WalletType] = None,
        wallet_subtype: Optional[WalletSubtype] = None,
        project_id: Optional[str] = None,
        vault_id: Optional[str] = None,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info("Calling WalletsApi->list_wallets")
                api_response = api_instance.list_wallets(
                    wallet_type=wallet_type,
                    wallet_subtype=wallet_subtype,
                    project_id=project_id,
                    vault_id=vault_id,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(f"Exception when calling WalletsApi->list_wallets: {e}\n")
                raise

    async def get_wallet_balance(
        self,
        wallet_id: str,
        token_ids: Optional[str] = None,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->list_token_balances_for_wallet for wallet_id: {wallet_id}"
                )
                api_response = api_instance.list_token_balances_for_wallet(
                    wallet_id,
                    token_ids=token_ids,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->list_token_balances_for_wallet: {e}\n"
                )
                raise

    async def get_wallet_transactions(
        self,
        wallet_id: str,
        types: Optional[str] = None,
        statuses: Optional[str] = None,
        chain_ids: Optional[str] = None,
        token_ids: Optional[str] = None,
        min_created_timestamp: Optional[int] = None,
        max_created_timestamp: Optional[int] = None,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info(
                    f"Calling TransactionsApi->list_transactions for wallet_id: {wallet_id}"
                )
                api_response = api_instance.list_transactions(
                    wallet_ids=wallet_id,
                    types=types,
                    statuses=statuses,
                    chain_ids=chain_ids,
                    token_ids=token_ids,
                    min_created_timestamp=min_created_timestamp,
                    max_created_timestamp=max_created_timestamp,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->list_transactions: {e}\n"
                )
                raise

    async def deposit_to_wallet(self, wallet_id: str, amount: float, token: str):
        # Note: Deposits are typically handled by generating an address and waiting for incoming transactions
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->create_address for wallet_id: {wallet_id}"
                )
                api_response = api_instance.create_address(wallet_id)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->create_address: {e}\n"
                )
                return None

    async def withdraw_from_wallet(
        self,
        wallet_id: str,
        amount: float,
        token: str,
        address: str,
        request_id: Optional[str] = None,
        memo: Optional[str] = None,
        fee_amount: Optional[float] = None,
        fee_token: Optional[str] = None,
        force_external: Optional[bool] = None,
        force_internal: Optional[bool] = None,
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                request_body = {
                    "wallet_id": wallet_id,
                    "token_id": token,
                    "amount": str(amount),
                    "to_address": address,
                    "request_id": request_id,
                    "memo": memo,
                    "fee_amount": str(fee_amount) if fee_amount is not None else None,
                    "fee_token": fee_token,
                    "force_external": force_external,
                    "force_internal": force_internal,
                }
                logger.info("Calling TransactionsApi->create_transfer_transaction")
                logger.info(f"Request body: {request_body}")
                api_response = api_instance.create_transfer_transaction(request_body)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->create_transfer_transaction: {e}\n"
                )
                raise

    async def handle_webhook(self, payload: dict):
        # Implement webhook handling logic based on the payload
        event_type = payload.get("type")
        logger.info(f"Handling webhook event: {event_type}")
        logger.info(f"Webhook payload: {payload}")
        if event_type == "transaction.created":
            # Handle new transaction
            pass
        elif event_type == "transaction.confirmed":
            # Handle confirmed transaction
            pass
        # Add more event types as needed

    async def create_new_address(
        self,
        wallet_id: str,
        chain_id: str,
        count: int = 1,
        encoding: Optional[str] = None,
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->create_address for wallet_id: {wallet_id}"
                )
                request_body = {
                    "chain_id": chain_id,
                    "count": count,
                    "encoding": encoding,
                }
                api_response = api_instance.create_address(wallet_id, request_body)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->create_address: {e}\n"
                )
                raise

    async def list_wallet_addresses(
        self,
        wallet_id: str,
        chain_ids: Optional[str],
        addresses: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->list_addresses for wallet_id: {wallet_id}"
                )
                api_response = api_instance.list_addresses(
                    wallet_id,
                    chain_ids=chain_ids,
                    addresses=addresses,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->list_addresses: {e}\n"
                )
                raise

    async def get_wallet_by_id(self, wallet_id: str):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->get_wallet_by_id for wallet_id: {wallet_id}"
                )
                api_response = api_instance.get_wallet_by_id(wallet_id)
                return api_response
            except ApiException as e:
                logger.error(f"Exception when calling WalletsApi->get_wallet: {e}\n")
                raise

    async def list_supported_chains(
        self,
        wallet_type: Optional[WalletType],
        wallet_subtype: Optional[WalletSubtype],
        chain_ids: Optional[str],
        token_list_id: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info("Calling WalletsApi->list_supported_chains")
                api_response = api_instance.list_supported_chains(
                    wallet_type=wallet_type,
                    wallet_subtype=wallet_subtype,
                    chain_ids=chain_ids,
                    token_list_id=token_list_id,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->list_supported_chains: {e}\n"
                )
                raise

    async def list_supported_tokens(
        self,
        wallet_type: Optional[WalletType],
        wallet_subtype: Optional[WalletSubtype],
        chain_ids: Optional[str],
        token_ids: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info("Calling WalletsApi->list_supported_tokens")
                api_response = api_instance.list_supported_tokens(
                    wallet_type=wallet_type,
                    wallet_subtype=wallet_subtype,
                    chain_ids=chain_ids,
                    token_ids=token_ids,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->list_supported_tokens: {e}\n"
                )
                raise

    async def check_address_validity(self, chain_id: str, address: str):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = WalletsApi(api_client)
            try:
                logger.info(
                    f"Calling WalletsApi->check_address_validity for chain_id: {chain_id}, address: {address}"
                )
                api_response = api_instance.check_address_validity(chain_id, address)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling WalletsApi->check_address_validity: {e}\n"
                )
                raise

    async def list_transactions(
        self,
        request_id: Optional[str],
        cobo_ids: Optional[str],
        transaction_ids: Optional[str],
        transaction_hashes: Optional[str],
        types: Optional[str],
        statuses: Optional[str],
        wallet_ids: Optional[str],
        chain_ids: Optional[str],
        token_ids: Optional[str],
        asset_ids: Optional[str],
        vault_id: Optional[str],
        project_id: Optional[str],
        min_created_timestamp: Optional[int],
        max_created_timestamp: Optional[int],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info("Calling TransactionsApi->list_transactions")
                api_response = api_instance.list_transactions(
                    request_id=request_id,
                    cobo_ids=cobo_ids,
                    transaction_ids=transaction_ids,
                    transaction_hashes=transaction_hashes,
                    types=types,
                    statuses=statuses,
                    wallet_ids=wallet_ids,
                    chain_ids=chain_ids,
                    token_ids=token_ids,
                    asset_ids=asset_ids,
                    vault_id=vault_id,
                    project_id=project_id,
                    min_created_timestamp=min_created_timestamp,
                    max_created_timestamp=max_created_timestamp,
                    limit=limit,
                    before=before,
                    after=after,
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->list_transactions: {e}\n"
                )
                raise

    async def get_transaction_by_id(self, transaction_id: str):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info(
                    f"Calling TransactionsApi->get_transaction for transaction_id: {transaction_id}"
                )
                api_response = api_instance.get_transaction_by_id(transaction_id)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->get_transaction: {e}\n"
                )
                raise

    async def create_transfer_transaction(
        self,
        request_id: str,
        source_wallet_id: str,
        source_address: str,
        destination_address: str,
        token_id: str,
        amount: str,
        fee_rate: Optional[str],
        max_fee: Optional[str],
        utxo_outputs: Optional[List[Dict[str, Any]]],
        memo: Optional[str],
        note: Optional[str],
        extra_parameters: Optional[Dict[str, Any]],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info("Calling TransactionsApi->create_transfer_transaction")
                request_body = {
                    "request_id": request_id,
                    "source_wallet_id": source_wallet_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                    "token_id": token_id,
                    "amount": amount,
                    "fee_rate": fee_rate,
                    "max_fee": max_fee,
                    "utxo_outputs": utxo_outputs,
                    "memo": memo,
                    "note": note,
                    "extra_parameters": extra_parameters,
                }
                api_response = api_instance.create_transfer_transaction(request_body)
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->create_transfer_transaction: {e}\n"
                )
                raise

    async def create_contract_call_transaction(
        self,
        request_id: str,
        source_wallet_id: str,
        source_address: str,
        destination_address: str,
        token_id: str,
        amount: str,
        calldata: str,
        fee_rate: Optional[str],
        max_fee: Optional[str],
        gas_limit: Optional[int],
        note: Optional[str],
        extra_parameters: Optional[Dict[str, Any]],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info("Calling TransactionsApi->create_contract_call_transaction")
                request_body = {
                    "request_id": request_id,
                    "source_wallet_id": source_wallet_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                    "token_id": token_id,
                    "amount": amount,
                    "calldata": calldata,
                    "fee_rate": fee_rate,
                    "max_fee": max_fee,
                    "gas_limit": gas_limit,
                    "note": note,
                    "extra_parameters": extra_parameters,
                }
                api_response = api_instance.create_contract_call_transaction(
                    request_body
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->create_contract_call_transaction: {e}\n"
                )
                raise

    async def create_message_sign_transaction(
        self,
        request_id: str,
        source_wallet_id: str,
        source_address: str,
        message: str,
        note: Optional[str],
        extra_parameters: Optional[Dict[str, Any]],
    ):
        with cobo_waas2.ApiClient(self.configuration) as api_client:
            api_instance = TransactionsApi(api_client)
            try:
                logger.info("Calling TransactionsApi->create_message_sign_transaction")
                request_body = {
                    "request_id": request_id,
                    "source_wallet_id": source_wallet_id,
                    "source_address": source_address,
                    "message": message,
                    "note": note,
                    "extra_parameters": extra_parameters,
                }
                api_response = api_instance.create_message_sign_transaction(
                    request_body
                )
                return api_response
            except ApiException as e:
                logger.error(
                    f"Exception when calling TransactionsApi->create_message_sign_transaction: {e}\n"
                )
                raise
