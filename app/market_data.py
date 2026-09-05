"""Unauthenticated Binance public market-data helpers for Sentinel v0.5."""

from __future__ import annotations

import requests


BINANCE_BASE_URL = "https://api.binance.com"
TRACKED_ASSETS = ("BTC", "ETH", "BNB")


def fetch_24h_ticker(asset: str) -> dict:
    """Return public 24-hour ticker data for an asset quoted in USDT."""

    symbol = f"{asset.upper()}USDT"
    response = requests.get(
        f"{BINANCE_BASE_URL}/api/v3/ticker/24hr",
        params={"symbol": symbol},
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()

    return {
        "asset": asset.upper(),
        "symbol": symbol,
        "price": float(data["lastPrice"]),
        "change_percent": float(data["priceChangePercent"]),
        "high": float(data["highPrice"]),
        "low": float(data["lowPrice"]),
        "volume": float(data["volume"]),
    }


def fetch_market_snapshot(assets: tuple[str, ...] = TRACKED_ASSETS) -> dict:
    """Fetch several public tickers and preserve per-asset errors gracefully."""

    snapshot: dict[str, dict] = {}

    for asset in assets:
        try:
            snapshot[asset] = {
                "ok": True,
                "data": fetch_24h_ticker(asset),
                "error": None,
            }
        except requests.RequestException as exc:
            snapshot[asset] = {
                "ok": False,
                "data": None,
                "error": str(exc),
            }
        except (KeyError, TypeError, ValueError) as exc:
            snapshot[asset] = {
                "ok": False,
                "data": None,
                "error": f"Unexpected Binance response: {exc}",
            }

    return snapshot
