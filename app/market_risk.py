"""Market-aware portfolio risk scoring for Binance Sentinel v0.6."""

from __future__ import annotations

from app.constitution import RiskConstitution
from app.risk_engine import STABLECOINS, allocations, risk_summary


def _risk_level(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MODERATE"
    return "LOW"


def market_aware_risk(
    portfolio: dict[str, float],
    constitution: RiskConstitution,
    market_snapshot: dict[str, dict],
) -> dict:
    """Combine portfolio structure with live 24h Binance market moves.

    The score is intentionally deterministic and explainable. It is not a
    prediction model and does not provide trading advice.
    """

    weights = allocations(portfolio)
    constitution_result = risk_summary(portfolio, constitution)

    score = 0.0
    reasons: list[str] = []

    # 1) Concentration risk: up to 40 points.
    if constitution_result["violations"]:
        score += 25.0
        max_excess_ratio = 0.0
        for violation in constitution_result["violations"]:
            limit = max(violation["limit"], 0.0001)
            excess_ratio = max(0.0, violation["allocation"] - limit) / limit
            max_excess_ratio = max(max_excess_ratio, excess_ratio)
        score += min(15.0, max_excess_ratio * 30.0)
        reasons.append("Portfolio concentration exceeds the Risk Constitution.")

    # 2) Stablecoin reserve risk: up to 20 points.
    stablecoin_weight = constitution_result["stablecoin_allocation"]
    stablecoin_minimum = constitution_result["stablecoin_minimum"]
    if stablecoin_weight < stablecoin_minimum:
        shortage = stablecoin_minimum - stablecoin_weight
        shortage_ratio = shortage / max(stablecoin_minimum, 0.0001)
        score += min(20.0, 10.0 + shortage_ratio * 10.0)
        reasons.append("Stablecoin reserve is below the configured minimum.")

    # 3) Live portfolio-weighted 24h move: up to 30 points for losses.
    weighted_change = 0.0
    covered_weight = 0.0
    largest_drop: tuple[str, float] | None = None

    for asset, weight in weights.items():
        if asset in STABLECOINS or weight <= 0:
            continue

        result = market_snapshot.get(asset)
        if not result or not result.get("ok") or not result.get("data"):
            continue

        change_percent = float(result["data"]["change_percent"])
        weighted_change += weight * change_percent
        covered_weight += weight

        if largest_drop is None or change_percent < largest_drop[1]:
            largest_drop = (asset, change_percent)

    if weighted_change < 0:
        score += min(30.0, abs(weighted_change) * 4.0)
        reasons.append(
            f"Tracked holdings have a portfolio-weighted 24h move of {weighted_change:.2f}%."
        )

    # 4) Extra shock flag for a sharp individual 24h drop: up to 10 points.
    if largest_drop is not None:
        asset, drop = largest_drop
        if drop <= -8.0:
            score += 10.0
            reasons.append(f"{asset} is down {abs(drop):.2f}% over 24h.")
        elif drop <= -4.0:
            score += 5.0
            reasons.append(f"{asset} is down {abs(drop):.2f}% over 24h.")

    score = min(100.0, round(score, 1))

    if not reasons:
        reasons.append("No major structural or live-market risk trigger is active.")

    return {
        "score": score,
        "level": _risk_level(score),
        "weighted_24h_change": weighted_change,
        "market_data_coverage": covered_weight,
        "largest_drop": largest_drop,
        "reasons": reasons,
    }
