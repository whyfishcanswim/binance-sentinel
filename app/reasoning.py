"""Explainable agent reasoning for Binance Sentinel v0.7.

This module deliberately keeps the reasoning deterministic. It converts the
portfolio, Risk Constitution, market-aware score, rebalance proposal, and stress
results into an auditable Observe -> Reason -> Plan -> Guardrail assessment.
No LLM or external AI API is required in v0.7.
"""

from __future__ import annotations


def build_agent_assessment(
    portfolio: dict[str, float],
    constitution_risk: dict,
    market_risk: dict,
    proposal: dict | None,
    stress_results: list[dict],
) -> dict:
    """Build a human-readable, auditable portfolio-risk assessment."""

    total = sum(portfolio.values())
    level = market_risk["level"]
    score = float(market_risk["score"])

    if level == "CRITICAL":
        priority = "IMMEDIATE REVIEW"
        headline = "Combined portfolio and market risk is critical."
    elif level == "HIGH":
        priority = "HIGH PRIORITY"
        headline = "Portfolio risk is elevated and should be reviewed."
    elif level == "MODERATE":
        priority = "MONITOR"
        headline = "Risk is moderate; monitor the portfolio and market conditions."
    else:
        priority = "NORMAL"
        headline = "No major combined risk trigger is active."

    observations: list[str] = [
        f"Portfolio value in this prototype is ${total:,.2f}.",
        f"Market-aware risk score is {score:.1f}/100 ({level}).",
        f"Portfolio-weighted tracked 24h move is {market_risk['weighted_24h_change']:.2f}%.",
    ]

    for violation in constitution_risk.get("violations", []):
        observations.append(
            f"{violation['asset']} allocation is {violation['allocation'] * 100:.1f}%, "
            f"above the {violation['limit'] * 100:.1f}% constitution limit."
        )

    stablecoin_allocation = float(constitution_risk["stablecoin_allocation"])
    stablecoin_minimum = float(constitution_risk["stablecoin_minimum"])
    if stablecoin_allocation < stablecoin_minimum:
        observations.append(
            f"Stablecoin allocation is {stablecoin_allocation * 100:.1f}%, below the "
            f"{stablecoin_minimum * 100:.1f}% minimum."
        )

    reasoning: list[str] = []
    if constitution_risk.get("violations"):
        reasoning.append(
            "Concentration risk is the first structural issue because one or more holdings violate the Risk Constitution."
        )

    if stablecoin_allocation < stablecoin_minimum:
        reasoning.append(
            "The stablecoin reserve is below its minimum, reducing the portfolio's configured defensive buffer."
        )

    if market_risk["weighted_24h_change"] < -3:
        reasoning.append(
            "Negative live market movement increases the urgency of existing structural risk."
        )
    elif market_risk["weighted_24h_change"] > 3:
        reasoning.append(
            "Positive short-term market movement does not cancel Risk Constitution violations."
        )

    if not reasoning:
        reasoning.append(
            "The portfolio structure and current tracked market movement do not create a major combined trigger."
        )

    plan: list[str] = []
    if proposal:
        plan.append(
            f"Review a simulated rebalance that reduces {proposal['asset']} by about "
            f"${proposal['reduce_by']:,.2f} and increases {proposal['destination']}."
        )
        plan.append(
            f"Re-check the portfolio after the simulated change to confirm {proposal['asset']} "
            f"moves toward the {proposal['target_allocation'] * 100:.1f}% limit."
        )
    else:
        plan.append("No concentration-driven rebalance is required by the current rules.")

    if stress_results:
        worst = min(stress_results, key=lambda item: item["drawdown"])
        plan.append(
            f"Keep the worst current stress scenario in view: {worst['name']} produces an estimated "
            f"{abs(worst['drawdown']) * 100:.1f}% portfolio decline."
        )

    guardrails = [
        "No trade is executed in v0.7.",
        "Risk Constitution rules override the reasoning layer.",
        "Live public market data is used only as evidence, not as a price prediction.",
        "Any future execution step must require explicit human approval.",
    ]

    return {
        "priority": priority,
        "headline": headline,
        "observations": observations,
        "reasoning": reasoning,
        "plan": plan,
        "guardrails": guardrails,
    }
