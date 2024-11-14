from typing import Callable, Awaitable, Any, Optional, List, Dict, Annotated

from fastapi import APIRouter, Request, Query, Body
from fastapi.responses import JSONResponse

from config import settings
from models.wallet import WalletType, WalletSubtype
from services.cobo_service import CoboService

router = APIRouter()
cobo_service = CoboService.get_instance(settings.COBO_API_SECRET, settings.COBO_ENV)


async def execute_service_call(
    service_method: Callable[..., Awaitable[Any]], *args, **kwargs
) -> JSONResponse:
    try:
        result = await service_method(*args, **kwargs)
        result_dict = result.to_dict() if hasattr(result, "to_dict") else result
        if isinstance(result_dict, dict) and "data" in result_dict:
            return JSONResponse(content={"status": "success", **result_dict})
        else:
            return JSONResponse(content={"status": "success", "data": result_dict})
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )


@router.get("/wallets")
async def list_wallets(
    wallet_type: Optional[WalletType] = None,
    wallet_subtype: Optional[WalletSubtype] = None,
    project_id: Optional[str] = None,
    vault_id: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.list_wallets,
        wallet_type,
        wallet_subtype,
        project_id,
        vault_id,
        limit,
        before,
        after,
    )


@router.get("/wallets/{wallet_id}")
async def get_wallet_by_id(wallet_id: str):
    return await execute_service_call(cobo_service.get_wallet_by_id, wallet_id)


@router.get("/wallets/{wallet_id}/balance")
async def get_wallet_balance(
    wallet_id: str,
    token_ids: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.get_wallet_balance, wallet_id, token_ids, limit, before, after
    )


@router.get("/wallets/{wallet_id}/transactions")
async def get_wallet_transactions(
    wallet_id: str,
    types: Optional[str] = None,
    statuses: Optional[str] = None,
    chain_ids: Optional[str] = None,
    token_ids: Optional[str] = None,
    min_created_timestamp: Optional[int] = None,
    max_created_timestamp: Optional[int] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.get_wallet_transactions,
        wallet_id,
        types,
        statuses,
        chain_ids,
        token_ids,
        min_created_timestamp,
        max_created_timestamp,
        limit,
        before,
        after,
    )


@router.post("/wallets/{wallet_id}/addresses")
async def create_new_address(
    wallet_id: str,
    chain_id: Annotated[str, Body()],
    count: Annotated[Optional[int], Body(ge=1, le=50)] = 1,
    encoding: Annotated[Optional[str], Body()] = None,
):
    return await execute_service_call(
        cobo_service.create_new_address, wallet_id, chain_id, count, encoding
    )


@router.get("/wallets/{wallet_id}/addresses")
async def list_wallet_addresses(
    wallet_id: str,
    chain_ids: Optional[str] = None,
    addresses: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.list_wallet_addresses,
        wallet_id,
        chain_ids,
        addresses,
        limit,
        before,
        after,
    )


@router.post("/wallets/{wallet_id}/withdraw")
async def withdraw_from_wallet(
    wallet_id: str,
    amount: Annotated[float, Body()],
    token: Annotated[str, Body()],
    address: Annotated[str, Body()],
    request_id: Annotated[Optional[str], Body()] = None,
    memo: Annotated[Optional[str], Body()] = None,
    fee_amount: Annotated[Optional[float], Body()] = None,
    fee_token: Annotated[Optional[str], Body()] = None,
    force_external: Annotated[Optional[bool], Body()] = None,
    force_internal: Annotated[Optional[bool], Body()] = None,
):
    return await execute_service_call(
        cobo_service.withdraw_from_wallet,
        wallet_id,
        amount,
        token,
        address,
        request_id,
        memo,
        fee_amount,
        fee_token,
        force_external,
        force_internal,
    )


@router.get("/wallets/chains")
async def list_supported_chains(
    wallet_type: Optional[WalletType] = None,
    wallet_subtype: Optional[WalletSubtype] = None,
    chain_ids: Optional[str] = None,
    token_list_id: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.list_supported_chains,
        wallet_type,
        wallet_subtype,
        chain_ids,
        token_list_id,
        limit,
        before,
        after,
    )


@router.get("/wallets/tokens")
async def list_supported_tokens(
    wallet_type: Optional[WalletType] = None,
    wallet_subtype: Optional[WalletSubtype] = None,
    chain_ids: Optional[str] = None,
    token_ids: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.list_supported_tokens,
        wallet_type,
        wallet_subtype,
        chain_ids,
        token_ids,
        limit,
        before,
        after,
    )


@router.get("/wallets/check_address_validity")
async def check_address_validity(chain_id: str = Query(...), address: str = Query(...)):
    return await execute_service_call(
        cobo_service.check_address_validity, chain_id, address
    )


@router.get("/transactions")
async def list_transactions(
    request_id: Optional[str] = None,
    cobo_ids: Optional[str] = None,
    transaction_ids: Optional[str] = None,
    transaction_hashes: Optional[str] = None,
    types: Optional[str] = None,
    statuses: Optional[str] = None,
    wallet_ids: Optional[str] = None,
    chain_ids: Optional[str] = None,
    token_ids: Optional[str] = None,
    asset_ids: Optional[str] = None,
    vault_id: Optional[str] = None,
    project_id: Optional[str] = None,
    min_created_timestamp: Optional[int] = None,
    max_created_timestamp: Optional[int] = None,
    limit: int = Query(default=10, ge=1, le=50),
    before: Optional[str] = None,
    after: Optional[str] = None,
):
    return await execute_service_call(
        cobo_service.list_transactions,
        request_id,
        cobo_ids,
        transaction_ids,
        transaction_hashes,
        types,
        statuses,
        wallet_ids,
        chain_ids,
        token_ids,
        asset_ids,
        vault_id,
        project_id,
        min_created_timestamp,
        max_created_timestamp,
        limit,
        before,
        after,
    )


@router.get("/transactions/{transaction_id}")
async def get_transaction_by_id(transaction_id: str):
    return await execute_service_call(
        cobo_service.get_transaction_by_id, transaction_id
    )


@router.post("/transactions/transfer")
async def create_transfer_transaction(
    request_id: Annotated[str, Body()],
    source_wallet_id: Annotated[str, Body()],
    source_address: Annotated[str, Body()],
    destination_address: Annotated[str, Body()],
    token_id: Annotated[str, Body()],
    amount: Annotated[str, Body()],
    fee_rate: Annotated[Optional[str], Body()] = None,
    max_fee: Annotated[Optional[str], Body()] = None,
    utxo_outputs: Annotated[Optional[List[Dict[str, Any]]], Body()] = None,
    memo: Annotated[Optional[str], Body()] = None,
    note: Annotated[Optional[str], Body()] = None,
    extra_parameters: Annotated[Optional[Dict[str, Any]], Body()] = None,
):
    return await execute_service_call(
        cobo_service.create_transfer_transaction,
        request_id,
        source_wallet_id,
        source_address,
        destination_address,
        token_id,
        amount,
        fee_rate,
        max_fee,
        utxo_outputs,
        memo,
        note,
        extra_parameters,
    )


@router.post("/transactions/contract_call")
async def create_contract_call_transaction(
    request_id: Annotated[str, Body()],
    source_wallet_id: Annotated[str, Body()],
    source_address: Annotated[str, Body()],
    destination_address: Annotated[str, Body()],
    token_id: Annotated[str, Body()],
    amount: Annotated[str, Body()],
    calldata: Annotated[str, Body()],
    fee_rate: Annotated[Optional[str], Body()] = None,
    max_fee: Annotated[Optional[str], Body()] = None,
    gas_limit: Annotated[Optional[int], Body()] = None,
    note: Annotated[Optional[str], Body()] = None,
    extra_parameters: Annotated[Optional[Dict[str, Any]], Body()] = None,
):
    return await execute_service_call(
        cobo_service.create_contract_call_transaction,
        request_id,
        source_wallet_id,
        source_address,
        destination_address,
        token_id,
        amount,
        calldata,
        fee_rate,
        max_fee,
        gas_limit,
        note,
        extra_parameters,
    )


@router.post("/transactions/message_sign")
async def create_message_sign_transaction(
    request_id: Annotated[str, Body()],
    source_wallet_id: Annotated[str, Body()],
    source_address: Annotated[str, Body()],
    message: Annotated[str, Body()],
    note: Annotated[Optional[str], Body()] = None,
    extra_parameters: Annotated[Optional[Dict[str, Any]], Body()] = None,
):
    return await execute_service_call(
        cobo_service.create_message_sign_transaction,
        request_id,
        source_wallet_id,
        source_address,
        message,
        note,
        extra_parameters,
    )


@router.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    return await execute_service_call(cobo_service.handle_webhook, payload)
