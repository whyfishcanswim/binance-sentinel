"""Scenario simulation engine for Binance Sentinel."""

from __future__ import annotations

SCENARIOS = {
    "Bitcoin drops 20%": {
        "description": "A BTC-led market correction scenario testing downside exposure.",
        "impact": -20,
    },
    "Market crash": {
        "description": "A severe market-wide drawdown scenario.",
        "impact": -35,
    },
    "Bull market": {
        "description": "A positive market expansion scenario.",
        "impact": 25,
    },
    "High volatility event": {
        "description": "A rapid volatility spike with uncertain direction.",
        "impact": -10,
    },
}


def simulate_scenario(portfolio_value: float, scenario: dict) -> dict:
    """Run a safe what-if simulation without trading."""

    before = portfolio_value
    impact = scenario["impact"]
    after = before * (1 + impact / 100)

    if impact <= -30:
        analysis = [
            "High downside exposure detected.",
            "Sentinel recommends reviewing concentration risk and reserve allocation.",
        ]
    elif impact < 0:
        analysis = [
            "Moderate downside scenario detected.",
            "Portfolio remains under simulated stress conditions.",
        ]
    else:
        analysis = [
            "Positive simulated market movement.",
            "Scenario indicates potential portfolio growth.",
        ]

    return {
        "before": before,
        "after": after,
        "impact": impact,
        "analysis": analysis,
    }
