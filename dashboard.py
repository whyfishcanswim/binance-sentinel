import streamlit as st

from app.constitution import RiskConstitution
from app.market_data import TRACKED_ASSETS, fetch_market_snapshot
from app.risk_engine import allocations, rebalance_proposal, risk_summary
from app.sample_data import SAMPLE_PORTFOLIO, STRESS_SCENARIOS
from app.stress_test import run_stress_test


st.set_page_config(
    page_title="Binance Sentinel",
    page_icon="🛡️",
    layout="wide",
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


st.title("Binance Sentinel")
st.caption("v0.5 — Safe dashboard with live public Binance market data")
st.info("Safe local mode: no Binance login, no API keys, and no trading.")

with st.sidebar:
    st.header("Risk Constitution")

    max_single_asset_pct = st.slider(
        "Maximum single-asset allocation",
        min_value=5,
        max_value=90,
        value=40,
        step=1,
    )

    min_stablecoin_pct = st.slider(
        "Minimum stablecoin allocation",
        min_value=0,
        max_value=90,
        value=15,
        step=1,
    )

    st.divider()
    st.header("Sample Portfolio")
    st.caption("Change these values to test Sentinel without connecting Binance.")

    portfolio = {}
    for asset, default_value in SAMPLE_PORTFOLIO.items():
        portfolio[asset] = st.number_input(
            f"{asset} value (USD)",
            min_value=0.0,
            value=float(default_value),
            step=10.0,
        )

constitution = RiskConstitution(
    max_single_asset=max_single_asset_pct / 100,
    min_stablecoin=min_stablecoin_pct / 100,
)

weights = allocations(portfolio)
total = sum(portfolio.values())
risk = risk_summary(portfolio, constitution)
proposal = rebalance_proposal(portfolio, constitution)

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Portfolio Value", money(total))
metric2.metric("Overall Risk", risk["level"])
metric3.metric("Stablecoin Allocation", pct(risk["stablecoin_allocation"]))
metric4.metric("Single-Asset Limit", pct(constitution.max_single_asset))

st.subheader("Live Binance Market Data")
st.caption("Public Binance data only. No account authentication is used.")

if st.button("Refresh Market Data"):
    st.cache_data.clear()


@st.cache_data(ttl=30)
def get_market_snapshot() -> dict:
    return fetch_market_snapshot(TRACKED_ASSETS)


market_snapshot = get_market_snapshot()
market_columns = st.columns(len(TRACKED_ASSETS))

for column, asset in zip(market_columns, TRACKED_ASSETS):
    result = market_snapshot[asset]
    with column:
        if result["ok"]:
            data = result["data"]
            st.metric(
                f"{asset}/USDT",
                money(data["price"]),
                f"{data['change_percent']:.2f}% (24h)",
            )
            st.caption(
                f"24h high {money(data['high'])} · low {money(data['low'])}"
            )
        else:
            st.error(f"{asset} market data unavailable")
            st.caption(result["error"])

st.subheader("Portfolio Allocation")
portfolio_rows = [
    {
        "Asset": asset,
        "Value": money(value),
        "Allocation": pct(weights.get(asset, 0.0)),
    }
    for asset, value in portfolio.items()
]
st.dataframe(portfolio_rows, width="stretch", hide_index=True)

chart_data = {asset: weight * 100 for asset, weight in weights.items()}
st.bar_chart(chart_data)

left, right = st.columns(2)

with left:
    st.subheader("Risk Check")

    if risk["level"] == "HIGH":
        st.error("Risk Constitution violation detected.")
    else:
        st.success("Portfolio is within the current Risk Constitution.")

    st.write(
        f"Stablecoin allocation: **{pct(risk['stablecoin_allocation'])}** "
        f"(minimum **{pct(risk['stablecoin_minimum'])}**)"
    )

    if risk["violations"]:
        st.write("**Concentration violations**")
        for violation in risk["violations"]:
            st.write(
                f"- {violation['asset']}: {pct(violation['allocation'])} "
                f"> limit {pct(violation['limit'])}"
            )
    else:
        st.write("No concentration-limit violations detected.")

with right:
    st.subheader("Suggested Rebalance")

    if proposal:
        st.warning(
            f"Reduce {proposal['asset']} by about {money(proposal['reduce_by'])} "
            f"and move that amount to {proposal['destination']}."
        )
        st.write(
            f"Target {proposal['asset']} allocation: "
            f"**{pct(proposal['target_allocation'])}**"
        )
        st.caption("Suggestion only. Sentinel v0.5 cannot place trades.")
    else:
        st.success("No concentration-driven rebalance is currently required.")

st.subheader("Stress Tests")
stress_rows = []

for name, scenario in STRESS_SCENARIOS.items():
    result = run_stress_test(portfolio, scenario)
    stress_rows.append(
        {
            "Scenario": name,
            "Before": money(result["before"]),
            "After": money(result["after"]),
            "Impact": pct(result["drawdown"]),
        }
    )

st.dataframe(stress_rows, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Sentinel v0.5 uses public Binance market data only. Binance Agent OS authentication and execution remain disabled."
)
