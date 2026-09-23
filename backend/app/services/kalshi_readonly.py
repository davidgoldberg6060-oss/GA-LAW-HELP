"""Read-only Kalshi account mirror.

Kalshi remains the source of truth. This module intentionally exposes no order,
transfer, deposit, withdrawal, or balance-mutation methods.
"""

from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


@dataclass(frozen=True)
class KalshiConfig:
    key_id: str
    private_key_pem: str
    rest_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"

    @classmethod
    def from_env(cls) -> "KalshiConfig":
        key_id = os.environ.get("KALSHI_API_KEY_ID", "").strip()
        private_key = os.environ.get("KALSHI_PRIVATE_KEY_PEM", "").replace("\\n", "\n").strip()
        base_url = os.environ.get(
            "KALSHI_REST_BASE_URL",
            "https://api.elections.kalshi.com/trade-api/v2",
        ).rstrip("/")
        if not key_id or not private_key:
            raise RuntimeError("Kalshi credentials are not configured")
        return cls(key_id=key_id, private_key_pem=private_key, rest_base_url=base_url)


class KalshiReadonlyClient:
    def __init__(self, config: KalshiConfig):
        self.config = config
        self._private_key = serialization.load_pem_private_key(
            config.private_key_pem.encode("utf-8"), password=None
        )

    def _headers(self, method: str, path: str) -> dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        # Kalshi signs timestamp + HTTP method + path (without query parameters).
        message = f"{timestamp}{method.upper()}{path.split('?', 1)[0]}".encode("utf-8")
        signature = self._private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        return {
            "KALSHI-ACCESS-KEY": self.config.key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("ascii"),
        }

    async def _get(self, path: str) -> dict:
        headers = self._headers("GET", path)
        async with httpx.AsyncClient(base_url=self.config.rest_base_url, timeout=10.0) as client:
            response = await client.get(path, headers=headers)
            response.raise_for_status()
            return response.json()

    async def balance(self) -> dict:
        return await self._get("/portfolio/balance")

    async def positions(self) -> dict:
        return await self._get("/portfolio/positions")

    async def snapshot(self) -> dict:
        balance = await self.balance()
        positions = await self.positions()
        return {
            "source": "kalshi",
            "read_only": True,
            "observed_at_ms": int(time.time() * 1000),
            "balance": balance,
            "positions": positions,
        }
