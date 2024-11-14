from enum import Enum
from typing import List

from pydantic import BaseModel


class WalletType(str, Enum):
    CUSTODIAL = "Custodial"
    MPC = "MPC"
    SMART_CONTRACT = "SmartContract"
    EXCHANGE = "Exchange"


class WalletSubtype(str, Enum):
    ASSET = "Asset"
    WEB3 = "Web3"
    MAIN = "Main"
    SUB = "Sub"
    ORG_CONTROLLED = "Org-Controlled"
    USER_CONTROLLED = "User-Controlled"
    SAFE_WALLET = "Safe{Wallet}"


class Token(BaseModel):
    symbol: str
    balance: float


class Wallet(BaseModel):
    id: str
    name: str
    tokens: List[Token]


class Transaction(BaseModel):
    id: str
    type: str
    amount: float
    token: str
    timestamp: int
