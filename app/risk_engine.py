"""Deterministic portfolio risk checks for Sentinel's safe prototype."""

MAX_SINGLE_ASSET = 0.40
MIN_STABLECOIN = 0.15
STABLECOINS = {"USDC", "USDT", "FDUSD"}


def portfolio_total(portfolio: dict[str, float]) -> float:
    return sum(portfolio.values())


def allocations(portfolio: dict[str, float]) -> dict[str, float]:
    total = portfolio_total(portfolio)
    if total <= 0:
        return {asset: 0.0 for asset in portfolio}
    return {asset: value / total for asset, value in portfolio.items()}


def concentration_violations(portfolio: dict[str, float]) -> list[dict]:
    result = []
    for asset, weight in allocations(portfolio).items():
        if asset not in STABLECOINS and weight > MAX_SINGLE_ASSET:
            result.append(
                {
                    "asset": asset,
                    "allocation": weight,
                    "limit": MAX_SINGLE_ASSET,
                }
            )
    return result


def stablecoin_allocation(portfolio: dict[str, float]) -> float:
    weights = allocations(portfolio)
    return sum(weights.get(asset, 0.0) for asset in STABLECOINS)


def risk_summary(portfolio: dict[str, float]) -> dict:
    violations = concentration_violations(portfolio)
    stablecoin_weight = stablecoin_allocation(portfolio)

    if violations or stablecoin_weight < MIN_STABLECOIN:
        level = "HIGH"
    else:
        level = "MODERATE"

    return {
        "level": level,
        "violations": violations,
        "stablecoin_allocation": stablecoin_weight,
        "stablecoin_minimum": MIN_STABLECOIN,
    }


def rebalance_proposal(portfolio: dict[str, float]) -> dict | None:
    total = portfolio_total(portfolio)
    if total <= 0:
        return None

    weights = allocations(portfolio)
    risky = [
        (asset, weight)
        for asset, weight in weights.items()
        if asset not in STABLECOINS and weight > MAX_SINGLE_ASSET
    ]
    if not risky:
        return None

    asset, weight = max(risky, key=lambda item: item[1])
    current_value = portfolio[asset]
    target_value = total * MAX_SINGLE_ASSET
    amount_to_reduce = max(0.0, current_value - target_value)

    return {
        "asset": asset,
        "current_allocation": weight,
        "target_allocation": MAX_SINGLE_ASSET,
        "reduce_by": amount_to_reduce,
        "destination": "USDC",
    }
