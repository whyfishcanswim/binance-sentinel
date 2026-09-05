"""Deterministic portfolio risk checks for Sentinel's safe prototype."""

from app.constitution import RiskConstitution

STABLECOINS = {"USDC", "USDT", "FDUSD"}


def portfolio_total(portfolio: dict[str, float]) -> float:
    return sum(portfolio.values())


def allocations(portfolio: dict[str, float]) -> dict[str, float]:
    total = portfolio_total(portfolio)
    if total <= 0:
        return {asset: 0.0 for asset in portfolio}
    return {asset: value / total for asset, value in portfolio.items()}


def concentration_violations(
    portfolio: dict[str, float],
    constitution: RiskConstitution,
) -> list[dict]:
    result = []
    for asset, weight in allocations(portfolio).items():
        if asset not in STABLECOINS and weight > constitution.max_single_asset:
            result.append(
                {
                    "asset": asset,
                    "allocation": weight,
                    "limit": constitution.max_single_asset,
                }
            )
    return result


def stablecoin_allocation(portfolio: dict[str, float]) -> float:
    weights = allocations(portfolio)
    return sum(weights.get(asset, 0.0) for asset in STABLECOINS)


def risk_summary(
    portfolio: dict[str, float],
    constitution: RiskConstitution,
) -> dict:
    violations = concentration_violations(portfolio, constitution)
    stablecoin_weight = stablecoin_allocation(portfolio)

    if violations or stablecoin_weight < constitution.min_stablecoin:
        level = "HIGH"
    else:
        level = "MODERATE"

    return {
        "level": level,
        "violations": violations,
        "stablecoin_allocation": stablecoin_weight,
        "stablecoin_minimum": constitution.min_stablecoin,
    }


def rebalance_proposal(
    portfolio: dict[str, float],
    constitution: RiskConstitution,
) -> dict | None:
    total = portfolio_total(portfolio)
    if total <= 0:
        return None

    weights = allocations(portfolio)
    risky = [
        (asset, weight)
        for asset, weight in weights.items()
        if asset not in STABLECOINS and weight > constitution.max_single_asset
    ]
    if not risky:
        return None

    asset, weight = max(risky, key=lambda item: item[1])
    current_value = portfolio[asset]
    target_value = total * constitution.max_single_asset
    amount_to_reduce = max(0.0, current_value - target_value)

    return {
        "asset": asset,
        "current_allocation": weight,
        "target_allocation": constitution.max_single_asset,
        "reduce_by": amount_to_reduce,
        "destination": constitution.destination_stablecoin,
    }
