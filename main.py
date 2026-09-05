from app.risk_engine import allocations, rebalance_proposal, risk_summary
from app.sample_data import SAMPLE_PORTFOLIO, STRESS_SCENARIOS
from app.stress_test import run_stress_test


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def show_portfolio() -> None:
    print("BINANCE SENTINEL — SAFE LOCAL PROTOTYPE\n")
    print("No Binance login. No API keys. No trading.\n")

    print("SAMPLE PORTFOLIO")
    print("----------------")

    weights = allocations(SAMPLE_PORTFOLIO)
    total = sum(SAMPLE_PORTFOLIO.values())

    for asset, value in SAMPLE_PORTFOLIO.items():
        print(f"{asset:<6} {money(value):>12}   {pct(weights[asset]):>7}")

    print(f"\nTotal: {money(total)}\n")


def show_risk() -> None:
    result = risk_summary(SAMPLE_PORTFOLIO)

    print("RISK CHECK")
    print("----------")
    print(f"Overall risk: {result['level']}")
    print(
        f"Stablecoin allocation: {pct(result['stablecoin_allocation'])} "
        f"(minimum {pct(result['stablecoin_minimum'])})"
    )

    if result["violations"]:
        print("\nConcentration violations:")
        for violation in result["violations"]:
            print(
                f"- {violation['asset']}: {pct(violation['allocation'])} "
                f"> limit {pct(violation['limit'])}"
            )
    else:
        print("\nNo concentration-limit violations detected.")

    proposal = rebalance_proposal(SAMPLE_PORTFOLIO)
    if proposal:
        print("\nSUGGESTED REBALANCE")
        print("-------------------")
        print(
            f"Reduce {proposal['asset']} by about {money(proposal['reduce_by'])} "
            f"and move that amount to {proposal['destination']}."
        )
        print(
            f"Target {proposal['asset']} allocation: "
            f"{pct(proposal['target_allocation'])}"
        )

    print()


def show_stress_tests() -> None:
    print("STRESS TESTS")
    print("------------")

    for name, scenario in STRESS_SCENARIOS.items():
        result = run_stress_test(SAMPLE_PORTFOLIO, scenario)
        print(name)
        print(f"  Before:   {money(result['before'])}")
        print(f"  After:    {money(result['after'])}")
        print(f"  Impact:   {pct(result['drawdown'])}")
        print()


def main() -> None:
    show_portfolio()
    show_risk()
    show_stress_tests()

    print("Prototype complete.")
    print("Next milestone: interactive Risk Constitution + simple dashboard.")


if __name__ == "__main__":
    main()
