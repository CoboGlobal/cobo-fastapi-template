import datetime
import json
import logging

import httpx
import jwt
from cobo_waas2.exceptions import ForbiddenException, UnauthorizedException
from fastapi import APIRouter
from pydantic import BaseModel

from app.cache import portal_user_payload_cache
from app.config import settings
from app.services.cobo_service import CoboService

router = APIRouter()

logger = logging.getLogger(__name__)


class GetTokenResponse(BaseModel):
    token: str
    refresh_token: str


class GetTokenRequest(BaseModel):
    token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    token: str


@router.post("", response_model=GetTokenResponse)
async def get_token(req: GetTokenRequest) -> GetTokenResponse:
    try:
        payload = await verify_jwt_token(req.token)
    except Exception as e:
        raise ForbiddenException(str(e))

    sub = payload["sub"]
    email = payload["email"]
    org_id = payload["org_id"]
    iss = payload["iss"]

    portal_user_payload_cache[f"{sub}-{org_id}"] = payload
    exp = datetime.datetime.now() + datetime.timedelta(minutes=30)
    access_token = jwt.encode(
        {
            "sub": sub,
            "email": email,
            "org_id": org_id,
            "iss": iss,
            "exp": int(exp.timestamp()),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    exp = datetime.datetime.now() + datetime.timedelta(days=1)
    refresh_access_token = jwt.encode(
        {
            "sub": sub,
            "email": email,
            "org_id": org_id,
            "refresh": True,
            "iss": iss,
            "exp": int(exp.timestamp()),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return GetTokenResponse(token=access_token, refresh_token=refresh_access_token)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(req: RefreshTokenRequest):
    try:
        payload_refresh_token = jwt.decode(
            req.refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
    except Exception as e:
        raise UnauthorizedException(str(e))

    sub = payload_refresh_token["sub"]
    org_id = payload_refresh_token["org_id"]
    user_payload = portal_user_payload_cache[f"{sub}-{org_id}"]
    if not user_payload:
        raise UnauthorizedException("User not found")

    exp = datetime.datetime.now() + datetime.timedelta(minutes=30)
    sub = user_payload["sub"]
    email = user_payload["email"]
    org_id = user_payload["org_id"]
    iss = user_payload["iss"]
    app_token = jwt.encode(
        {
            "sub": sub,
            "email": email,
            "org_id": org_id,
            "iss": iss,
            "exp": int(exp.timestamp()),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    return RefreshTokenResponse(token=app_token)


@router.get(
    "/callback",
)
async def organization_authorization_callback(
    approval_result: int,
    org_id: str,
):
    if approval_result != 1:
        logger.error(
            f"organization_authorization_callback failed, approval_result: {approval_result}"
        )
        return dict(success=True)

    await CoboService.set_token_by_org_id(org_id)
    return dict(success=True)


async def get_public_key(token_header):
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.jks_url)
        response.raise_for_status()
    jwks = json.loads(response.text)

    for key in jwks["keys"]:
        if key["kid"] == token_header["kid"]:
            return jwt.get_algorithm_by_name(token_header["alg"]).from_jwk(
                json.dumps(key)
            )
    return None


async def verify_jwt_token(token):
    try:
        headers = jwt.get_unverified_header(token)

        public_key = await get_public_key(headers)
        if public_key is None:
            return None

        alg = headers["alg"]

        payload = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            audience=settings.COBO_APP_CLIENT_ID,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
                "require_exp": True,
                "require_iat": True,
                "require_nbf": True,
            },
        )
        return payload
    except jwt.exceptions.InvalidTokenError as e:
        raise ForbiddenException(str(e))
