"""Portfolio stress testing for Sentinel's safe prototype."""


def run_stress_test(portfolio: dict[str, float], scenario: dict[str, float]) -> dict:
    before = sum(portfolio.values())
    after_values = {}

    for asset, value in portfolio.items():
        shock = scenario.get(asset, 0.0)
        after_values[asset] = value * (1 + shock)

    after = sum(after_values.values())
    drawdown = 0.0 if before <= 0 else (after - before) / before

    return {
        "before": before,
        "after": after,
        "drawdown": drawdown,
        "after_values": after_values,
    }
