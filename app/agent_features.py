"""Additional experience features for Binance Sentinel.

These features keep Sentinel focused on being a portfolio guardian rather than a
competition demo: explainability, confidence, and decision transparency.
"""


def generate_guardian_summary(assessment: dict, market_risk: dict) -> dict:
    """Create a concise human-facing agent report."""

    return {
        "status": market_risk.get("level", "UNKNOWN"),
        "confidence": min(95, max(50, int(100 - market_risk.get("score", 50) / 2))),
        "headline": assessment.get("headline", "Portfolio analysis completed."),
        "next_step": (
            assessment.get("plan", ["Continue monitoring."])[0]
            if assessment.get("plan")
            else "Continue monitoring."
        ),
        "safety": "Analysis only. No autonomous trading execution is enabled.",
    }


def create_agent_timeline(assessment: dict) -> list[dict]:
    """Return an agent trace suitable for a UI timeline."""

    return [
        {"stage": "Observe", "detail": item}
        for item in assessment.get("observations", [])
    ] + [
        {"stage": "Reason", "detail": item}
        for item in assessment.get("reasoning", [])
    ] + [
        {"stage": "Plan", "detail": item}
        for item in assessment.get("plan", [])
    ]
