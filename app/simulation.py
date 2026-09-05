"""Simulated rebalance preview for Binance Sentinel v0.8."""

from __future__ import annotations

from copy import deepcopy

from app.constitution import RiskConstitution
from app.market_risk import market_aware_risk
from app.risk_engine import allocations, risk_summary
from app.stress_test import run_stress_test


def apply_rebalance_simulation(
    portfolio: dict[str, float],
    proposal: dict | None,
) -> dict[str, float]:
    """Return a simulated portfolio after applying the proposed rebalance.

    No external action is performed. The function only moves value between
    assets in memory.
    """

    simulated = deepcopy(portfolio)

    if not proposal:
        return simulated

    source = proposal["asset"]
    destination = proposal["destination"]
    requested_amount = max(0.0, float(proposal["reduce_by"]))
    available_amount = max(0.0, float(simulated.get(source, 0.0)))
    amount = min(requested_amount, available_amount)

    simulated[source] = available_amount - amount
    simulated[destination] = float(simulated.get(destination, 0.0)) + amount

    return simulated


def build_rebalance_preview(
    portfolio: dict[str, float],
    proposal: dict | None,
    constitution: RiskConstitution,
    market_snapshot: dict[str, dict],
    stress_scenarios: dict[str, dict[str, float]],
) -> dict:
    """Compare current and simulated portfolio risk side by side."""

    before_portfolio = deepcopy(portfolio)
    after_portfolio = apply_rebalance_simulation(portfolio, proposal)

    before_constitution = risk_summary(before_portfolio, constitution)
    after_constitution = risk_summary(after_portfolio, constitution)

    before_market = market_aware_risk(
        before_portfolio,
        constitution,
        market_snapshot,
    )
    after_market = market_aware_risk(
        after_portfolio,
        constitution,
        market_snapshot,
    )

    before_weights = allocations(before_portfolio)
    after_weights = allocations(after_portfolio)

    stress_comparison = []
    for name, scenario in stress_scenarios.items():
        before_stress = run_stress_test(before_portfolio, scenario)
        after_stress = run_stress_test(after_portfolio, scenario)
        stress_comparison.append(
            {
                "name": name,
                "before_drawdown": before_stress["drawdown"],
                "after_drawdown": after_stress["drawdown"],
                "before_after_value": before_stress["after"],
                "after_after_value": after_stress["after"],
            }
        )

    assets = sorted(set(before_portfolio) | set(after_portfolio))
    allocation_changes = []
    for asset in assets:
        allocation_changes.append(
            {
                "asset": asset,
                "before_value": float(before_portfolio.get(asset, 0.0)),
                "after_value": float(after_portfolio.get(asset, 0.0)),
                "before_allocation": float(before_weights.get(asset, 0.0)),
                "after_allocation": float(after_weights.get(asset, 0.0)),
            }
        )

    score_change = round(after_market["score"] - before_market["score"], 1)
    violations_change = (
        len(after_constitution["violations"])
        - len(before_constitution["violations"])
    )

    if not proposal:
        verdict = "No rebalance proposal is currently available to simulate."
    elif score_change < 0 or violations_change < 0:
        verdict = "The simulated rebalance improves the current risk profile."
    elif score_change == 0 and violations_change == 0:
        verdict = "The simulated rebalance does not materially change the current risk profile."
    else:
        verdict = "The simulated rebalance does not improve the current risk profile."

    return {
        "before_portfolio": before_portfolio,
        "after_portfolio": after_portfolio,
        "before_constitution": before_constitution,
        "after_constitution": after_constitution,
        "before_market": before_market,
        "after_market": after_market,
        "score_change": score_change,
        "violations_change": violations_change,
        "allocation_changes": allocation_changes,
        "stress_comparison": stress_comparison,
        "verdict": verdict,
    }
