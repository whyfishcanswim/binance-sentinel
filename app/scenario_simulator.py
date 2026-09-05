"""What-if scenario simulation engine for Binance Sentinel.

This module lets Sentinel estimate portfolio impact under hypothetical market
conditions without executing trades or connecting to an exchange account.
"""

from __future__ import annotations


DEFAULT_SCENARIOS = {
    "Bitcoin drops 20%": {
        "BTC": -0.20,
        "ETH": -0.15,
        "BNB": -0.10,
    },
    "Market crash": {
        "BTC": -0.30,
        "ETH": -0.35,
        "BNB": -0.40,
    },
    "Bull market": {
        "BTC": 0.20,
        "ETH": 0.25,
        "BNB": 0.30,
    },
    "High volatility event": {
        "BTC": -0.10,
        "ETH": -0.20,
        "BNB": -0.25,
    },
}

SCENARIOS = DEFAULT_SCENARIOS


def simulate_market_event(portfolio: dict[str, float], scenario: dict[str, float]) -> dict:
    """Apply hypothetical percentage moves to a portfolio."""

    before = sum(portfolio.values())
    after = 0.0
    changes = []

    for asset, value in portfolio.items():
        movement = scenario.get(asset, 0.0)
        new_value = value * (1 + movement)
        after += new_value
        changes.append(
            {
                "asset": asset,
                "before": value,
                "after": new_value,
                "change_percent": movement * 100,
            }
        )

    return {
        "before_value": before,
        "after_value": after,
        "absolute_change": after - before,
        "percentage_change": ((after - before) / before * 100) if before else 0,
        "changes": changes,
    }


# Compatibility wrapper expected by Scenario Lab

def simulate_scenario(portfolio: dict[str, float], scenario: dict[str, float]) -> dict:
    """Run a named scenario simulation through the Sentinel engine."""
    return simulate_market_event(portfolio, scenario)


def build_scenario_explanation(result: dict, scenario_name: str) -> str:
    """Generate a concise Sentinel-style explanation."""

    impact = result["percentage_change"]

    if impact <= -20:
        level = "severe downside exposure"
    elif impact < -10:
        level = "elevated downside exposure"
    elif impact < 0:
        level = "limited downside impact"
    else:
        level = "positive portfolio movement"

    return (
        f"Under '{scenario_name}', Sentinel estimates {impact:+.1f}% portfolio impact. "
        f"This represents {level}. The result is a simulation only and does not execute any action."
    )
