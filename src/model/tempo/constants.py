from typing import Protocol
from primp import AsyncClient
from eth_account import Account

from src.model.onchain.web3_custom import Web3Custom
from src.utils.config import Config


TEMPO_TOKENS = [
    {"symbol": "AlphaUSD", "address": "0x20c0000000000000000000000000000000000001", "decimals": 6},
    {"symbol": "BetaUSD", "address": "0x20c0000000000000000000000000000000000002", "decimals": 6},
    {"symbol": "ThetaUSD", "address": "0x20c0000000000000000000000000000000000003", "decimals": 6},
]

# Tempo DEX (Built-in AMM) Precompile Address
DEX_CONTRACT_ADDRESS = "0xDEc0000000000000000000000000000000000000"

# PathUSD (Quote Token) Address
PATHUSD_ADDRESS = "0x20C0000000000000000000000000000000000000"


class TempoProtocol(Protocol):
    """Protocol class for Tempo type hints to avoid circular imports"""

    account_index: int
    session: AsyncClient
    web3: Web3Custom
    config: Config
    wallet: Account
    proxy: str



ERC20_TRANSFER_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]

# DEX ABI for swapping tokens
DEX_SWAP_ABI = [
    {
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountIn", "type": "uint128"},
            {"name": "minAmountOut", "type": "uint128"},
        ],
        "name": "swapExactAmountIn",
        "outputs": [{"name": "amountOut", "type": "uint128"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountOut", "type": "uint128"},
            {"name": "maxAmountIn", "type": "uint128"},
        ],
        "name": "swapExactAmountOut",
        "outputs": [{"name": "amountIn", "type": "uint128"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountIn", "type": "uint128"},
        ],
        "name": "quoteSwapExactAmountIn",
        "outputs": [{"name": "amountOut", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "amountOut", "type": "uint128"},
        ],
        "name": "quoteSwapExactAmountOut",
        "outputs": [{"name": "amountIn", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
]
