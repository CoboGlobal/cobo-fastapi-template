from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi import status
from jwt import InvalidTokenError

from app.cache import portal_user_payload_cache
from app.config import settings


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def token_header(Authorization: str = Header(...)):
    scheme, _, param = Authorization.partition(" ")
    if scheme != "Bearer":
        raise credentials_exception
    return param


async def get_current_user(token: Annotated[str, Depends(token_header)]):

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        org_id = payload.get("org_id")
        if sub is None or org_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user_payload = portal_user_payload_cache.get(f"{sub}-{org_id}")
    if user_payload is None:
        raise credentials_exception
    return user_payload


async def get_org_id(user_payload=Depends(get_current_user)):
    return user_payload["org_id"]
