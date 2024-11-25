import logging
from typing import Optional, List, Dict, Any

import cobo_waas2

# %if app_type == portal
from cobo_waas2 import OAuthApi, Configuration

# %else
from cobo_waas2 import Configuration

# %endif
from cobo_waas2.api import WalletsApi, TransactionsApi
from cobo_waas2.exceptions import ApiException
from cobo_waas2.models import WalletType, WalletSubtype

# %if app_type == portal
from app.cache import portal_org_token_cache

# %endif
from app.config import settings

logger = logging.getLogger(__name__)


class CoboApiClient(cobo_waas2.ApiClient):
    def __init__(
        self,
        # %if app_type == portal
        access_token: Optional[str] = None,
        # %endif
    ) -> None:
        # %if app_type == portal
        api_private_key = settings.COBO_APP_SECRET
        # %else
        api_private_key = settings.COBO_API_SECRET
        # %endif
        configuration = Configuration(
            api_private_key,
            host=settings.api_host,
            # %if app_type == portal
            access_token=access_token
            # %endif
        )
        super().__init__(configuration)
        # %if app_type == portal
        if access_token:
            self.default_headers[
                "Authorization"
            ] = f"Bearer {configuration.access_token}"
        # %endif


class CoboService:
    cobo_api_client: cobo_waas2.ApiClient = CoboApiClient()

    # %if app_type == portal
    @classmethod
    async def set_token_by_org_id(cls, org_id: str):
        resp = await CoboService.oauth_token(org_id)
        access_token = resp.access_token
        refresh_token = resp.refresh_token
        portal_org_token_cache[org_id] = dict(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        CoboService.set_auth_access_token(access_token)

    @classmethod
    def set_auth_access_token(cls, access_token: str):
        cls.cobo_api_client = CoboApiClient(access_token=access_token)

    @classmethod
    async def oauth_token(cls, org_id: str):
        api_instance = OAuthApi(cls.cobo_api_client)
        try:
            logger.info("Calling OAuthApi -> get_token")
            return api_instance.get_token(
                client_id=settings.COBO_APP_CLIENT_ID,
                org_id=org_id,
                grant_type="org_implicit",
            )
        except ApiException as e:
            logger.error(f"Exception when calling OAuthApi -> get_token: {e}\n")
            raise

    # %endif

    @classmethod
    async def list_wallets(
        cls,
        wallet_type: Optional[WalletType] = None,
        wallet_subtype: Optional[WalletSubtype] = None,
        project_id: Optional[str] = None,
        vault_id: Optional[str] = None,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info("Calling WalletsApi -> list_wallets")
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
            logger.error(f"Exception when calling WalletsApi -> list_wallets: {e}\n")
            raise

    @classmethod
    async def get_wallet_balance(
        cls,
        wallet_id: str,
        token_ids: Optional[str] = None,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> list_token_balances_for_wallet for wallet_id: {wallet_id}"
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
                f"Exception when calling WalletsApi -> list_token_balances_for_wallet: {e}\n"
            )
            raise

    @classmethod
    async def get_wallet_transactions(
        cls,
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
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling TransactionsApi -> list_transactions for wallet_id: {wallet_id}"
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
                f"Exception when calling TransactionsApi -> list_transactions: {e}\n"
            )
            raise

    @classmethod
    async def deposit_to_wallet(cls, wallet_id: str, amount: float, token: str):
        # Note: Deposits are typically handled by generating an address and waiting for incoming transactions
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> create_address for wallet_id: {wallet_id}"
            )
            api_response = api_instance.create_address(wallet_id)
            return api_response
        except ApiException as e:
            logger.error(f"Exception when calling WalletsApi -> create_address: {e}\n")
            return None

    @classmethod
    async def withdraw_from_wallet(
        cls,
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
        api_instance = TransactionsApi(cls.cobo_api_client)
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
            logger.info("Calling TransactionsApi -> create_transfer_transaction")
            logger.info(f"Request body: {request_body}")
            api_response = api_instance.create_transfer_transaction(request_body)
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling TransactionsApi -> create_transfer_transaction: {e}\n"
            )
            raise

    @classmethod
    async def handle_webhook(cls, payload: dict):
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

    @classmethod
    async def create_new_address(
        cls,
        wallet_id: str,
        chain_id: str,
        count: int = 1,
        encoding: Optional[str] = None,
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> create_address for wallet_id: {wallet_id}"
            )
            request_body = {
                "chain_id": chain_id,
                "count": count,
                "encoding": encoding,
            }
            api_response = api_instance.create_address(wallet_id, request_body)
            return api_response
        except ApiException as e:
            logger.error(f"Exception when calling WalletsApi -> create_address: {e}\n")
            raise

    @classmethod
    async def list_wallet_addresses(
        cls,
        wallet_id: str,
        chain_ids: Optional[str],
        addresses: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> list_addresses for wallet_id: {wallet_id}"
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
            logger.error(f"Exception when calling WalletsApi -> list_addresses: {e}\n")
            raise

    @classmethod
    async def get_wallet_by_id(cls, wallet_id: str):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> get_wallet_by_id for wallet_id: {wallet_id}"
            )
            api_response = api_instance.get_wallet_by_id(wallet_id)
            return api_response
        except ApiException as e:
            logger.error(f"Exception when calling WalletsApi -> get_wallet: {e}\n")
            raise

    @classmethod
    async def list_supported_chains(
        cls,
        wallet_type: Optional[WalletType],
        wallet_subtype: Optional[WalletSubtype],
        chain_ids: Optional[str],
        token_list_id: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info("Calling WalletsApi -> list_supported_chains")
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
                f"Exception when calling WalletsApi -> list_supported_chains: {e}\n"
            )
            raise

    @classmethod
    async def list_supported_tokens(
        cls,
        wallet_type: Optional[WalletType],
        wallet_subtype: Optional[WalletSubtype],
        chain_ids: Optional[str],
        token_ids: Optional[str],
        limit: int,
        before: Optional[str],
        after: Optional[str],
    ):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info("Calling WalletsApi -> list_supported_tokens")
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
                f"Exception when calling WalletsApi -> list_supported_tokens: {e}\n"
            )
            raise

    @classmethod
    async def check_address_validity(cls, chain_id: str, address: str):
        api_instance = WalletsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling WalletsApi -> check_address_validity for chain_id: {chain_id}, address: {address}"
            )
            api_response = api_instance.check_address_validity(chain_id, address)
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling WalletsApi -> check_address_validity: {e}\n"
            )
            raise

    @classmethod
    async def list_transactions(
        cls,
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
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info("Calling TransactionsApi -> list_transactions")
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
                f"Exception when calling TransactionsApi -> list_transactions: {e}\n"
            )
            raise

    @classmethod
    async def get_transaction_by_id(cls, transaction_id: str):
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info(
                f"Calling TransactionsApi->get_transaction for transaction_id: {transaction_id}"
            )
            api_response = api_instance.get_transaction_by_id(transaction_id)
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling TransactionsApi -> get_transaction: {e}\n"
            )
            raise

    @classmethod
    async def create_transfer_transaction(
        cls,
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
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info("Calling TransactionsApi -> create_transfer_transaction")
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
                f"Exception when calling TransactionsApi -> create_transfer_transaction: {e}\n"
            )
            raise

    @classmethod
    async def create_contract_call_transaction(
        cls,
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
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info("Calling TransactionsApi -> create_contract_call_transaction")
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
            api_response = api_instance.create_contract_call_transaction(request_body)
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling TransactionsApi -> create_contract_call_transaction: {e}\n"
            )
            raise

    @classmethod
    async def create_message_sign_transaction(
        cls,
        request_id: str,
        source_wallet_id: str,
        source_address: str,
        message: str,
        note: Optional[str],
        extra_parameters: Optional[Dict[str, Any]],
    ):
        api_instance = TransactionsApi(cls.cobo_api_client)
        try:
            logger.info("Calling TransactionsApi -> create_message_sign_transaction")
            request_body = {
                "request_id": request_id,
                "source_wallet_id": source_wallet_id,
                "source_address": source_address,
                "message": message,
                "note": note,
                "extra_parameters": extra_parameters,
            }
            api_response = api_instance.create_message_sign_transaction(request_body)
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling TransactionsApi -> create_message_sign_transaction: {e}\n"
            )
            raise
