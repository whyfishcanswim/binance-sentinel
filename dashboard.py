import streamlit as st

from app.constitution import RiskConstitution
from app.market_data import TRACKED_ASSETS, fetch_market_snapshot
from app.market_risk import market_aware_risk
from app.reasoning import build_agent_assessment
from app.risk_engine import allocations, rebalance_proposal, risk_summary
from app.sample_data import SAMPLE_PORTFOLIO, STRESS_SCENARIOS
from app.simulation import build_rebalance_preview
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


@st.cache_data(ttl=30)
def get_market_snapshot() -> dict:
    return fetch_market_snapshot(TRACKED_ASSETS)


st.title("Binance Sentinel")
st.caption("v0.8 — Simulated rebalance preview")
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
constitution_risk = risk_summary(portfolio, constitution)
proposal = rebalance_proposal(portfolio, constitution)

st.subheader("Live Binance Market Data")
st.caption("Public Binance data only. No account authentication is used.")

if st.button("Refresh Market Data"):
    st.cache_data.clear()

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

market_risk = market_aware_risk(portfolio, constitution, market_snapshot)

stress_results = []
for name, scenario in STRESS_SCENARIOS.items():
    result = run_stress_test(portfolio, scenario)
    result["name"] = name
    stress_results.append(result)

assessment = build_agent_assessment(
    portfolio,
    constitution_risk,
    market_risk,
    proposal,
    stress_results,
)

preview = build_rebalance_preview(
    portfolio,
    proposal,
    constitution,
    market_snapshot,
    STRESS_SCENARIOS,
)

st.subheader("Market-Aware Risk")
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Portfolio Value", money(total))
metric2.metric("Risk Level", market_risk["level"])
metric3.metric("Risk Score", f"{market_risk['score']:.1f} / 100")
metric4.metric(
    "Weighted 24h Move",
    f"{market_risk['weighted_24h_change']:.2f}%",
)

if market_risk["level"] == "CRITICAL":
    st.error("Sentinel detects critical combined portfolio and market risk.")
elif market_risk["level"] == "HIGH":
    st.warning("Sentinel detects elevated combined portfolio and market risk.")
elif market_risk["level"] == "MODERATE":
    st.info("Sentinel detects moderate combined portfolio and market risk.")
else:
    st.success("Sentinel currently detects low combined portfolio and market risk.")

st.write("**Why Sentinel assigned this score**")
for reason in market_risk["reasons"]:
    st.write(f"- {reason}")

st.caption(
    f"Live market-data coverage of the sample portfolio: "
    f"{pct(market_risk['market_data_coverage'])}. "
    "The score is deterministic and explainable; it is not a price prediction."
)

st.subheader("Sentinel Agent Assessment")
agent1, agent2 = st.columns([1, 3])
with agent1:
    st.metric("Action Priority", assessment["priority"])
with agent2:
    st.write(f"### {assessment['headline']}")

with st.expander("Observe — what Sentinel sees", expanded=True):
    for item in assessment["observations"]:
        st.write(f"- {item}")

with st.expander("Reason — how Sentinel interprets it", expanded=True):
    for item in assessment["reasoning"]:
        st.write(f"- {item}")

with st.expander("Plan — what Sentinel recommends reviewing", expanded=True):
    for item in assessment["plan"]:
        st.write(f"- {item}")

with st.expander("Guardrails — what Sentinel is not allowed to do"):
    for item in assessment["guardrails"]:
        st.write(f"- {item}")

st.subheader("Simulated Rebalance Preview")
st.caption("This is a what-if calculation only. No trade is sent anywhere.")

if proposal:
    st.write(
        f"Simulated action: reduce **{proposal['asset']}** by about "
        f"**{money(proposal['reduce_by'])}** and move that value to "
        f"**{proposal['destination']}**."
    )

    before_col, after_col, change_col = st.columns(3)
    before_col.metric(
        "Before Risk Score",
        f"{preview['before_market']['score']:.1f} / 100",
        preview["before_market"]["level"],
    )
    after_col.metric(
        "After Risk Score",
        f"{preview['after_market']['score']:.1f} / 100",
        preview["after_market"]["level"],
    )
    change_col.metric(
        "Score Change",
        f"{preview['score_change']:+.1f}",
    )

    if preview["score_change"] < 0 or preview["violations_change"] < 0:
        st.success(preview["verdict"])
    elif preview["score_change"] > 0 or preview["violations_change"] > 0:
        st.error(preview["verdict"])
    else:
        st.info(preview["verdict"])

    comparison_rows = []
    for row in preview["allocation_changes"]:
        comparison_rows.append(
            {
                "Asset": row["asset"],
                "Before Value": money(row["before_value"]),
                "After Value": money(row["after_value"]),
                "Before Allocation": pct(row["before_allocation"]),
                "After Allocation": pct(row["after_allocation"]),
            }
        )

    st.write("**Before vs After Allocation**")
    st.dataframe(comparison_rows, width="stretch", hide_index=True)

    st.write("**Stress-test comparison**")
    stress_preview_rows = []
    for row in preview["stress_comparison"]:
        stress_preview_rows.append(
            {
                "Scenario": row["name"],
                "Before Drawdown": pct(row["before_drawdown"]),
                "After Drawdown": pct(row["after_drawdown"]),
                "Before Scenario Value": money(row["before_after_value"]),
                "After Scenario Value": money(row["after_after_value"]),
            }
        )

    st.dataframe(stress_preview_rows, width="stretch", hide_index=True)
else:
    st.success("No concentration-driven rebalance is currently required, so there is nothing to simulate.")

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
    st.subheader("Risk Constitution Check")

    if constitution_risk["level"] == "HIGH":
        st.error("Risk Constitution violation detected.")
    else:
        st.success("Portfolio is within the current Risk Constitution.")

    st.write(
        f"Stablecoin allocation: **{pct(constitution_risk['stablecoin_allocation'])}** "
        f"(minimum **{pct(constitution_risk['stablecoin_minimum'])}**)"
    )

    if constitution_risk["violations"]:
        st.write("**Concentration violations**")
        for violation in constitution_risk["violations"]:
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
        st.caption("Suggestion only. Sentinel v0.8 cannot place trades.")
    else:
        st.success("No concentration-driven rebalance is currently required.")

st.subheader("Stress Tests")
stress_rows = [
    {
        "Scenario": result["name"],
        "Before": money(result["before"]),
        "After": money(result["after"]),
        "Impact": pct(result["drawdown"]),
    }
    for result in stress_results
]

st.dataframe(stress_rows, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Sentinel v0.8 adds a simulated before-vs-after rebalance preview. "
    "It executes nothing. Binance Agent OS authentication and real execution remain disabled."
)
