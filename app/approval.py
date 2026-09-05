"""Human approval workflow primitives for Binance Sentinel v0.9.

This module creates a deterministic action request for the simulated rebalance.
It never connects to Binance and never executes a trade.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def build_action_request(
    portfolio: dict[str, float],
    proposal: dict | None,
    preview: dict,
) -> dict | None:
    """Create a stable approval request for the current simulated action."""

    if not proposal:
        return None

    payload = {
        "portfolio": {key: round(float(value), 8) for key, value in sorted(portfolio.items())},
        "proposal": {
            "asset": proposal["asset"],
            "destination": proposal["destination"],
            "reduce_by": round(float(proposal["reduce_by"]), 8),
            "target_allocation": round(float(proposal["target_allocation"]), 8),
        },
        "before_score": round(float(preview["before_market"]["score"]), 1),
        "after_score": round(float(preview["after_market"]["score"]), 1),
    }

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    action_id = hashlib.sha256(encoded).hexdigest()[:12].upper()

    return {
        "id": action_id,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_asset": proposal["asset"],
        "destination_asset": proposal["destination"],
        "amount_usd": float(proposal["reduce_by"]),
        "target_allocation": float(proposal["target_allocation"]),
        "before_score": float(preview["before_market"]["score"]),
        "after_score": float(preview["after_market"]["score"]),
        "score_change": float(preview["score_change"]),
        "simulated_after_portfolio": preview["after_portfolio"],
    }


def decision_record(action_request: dict, decision: str) -> dict:
    """Return an immutable-style local decision record."""

    normalized = decision.upper().strip()
    if normalized not in {"APPROVED", "REJECTED"}:
        raise ValueError("Decision must be APPROVED or REJECTED.")

    return {
        **action_request,
        "status": normalized,
        "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
