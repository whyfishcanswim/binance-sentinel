import streamlit as st

from app.agent_os import skills_hub_status
from app.approval import build_action_request, decision_record
from app.constitution import RiskConstitution
from app.demo_scenarios import DEFAULT_DEMO_SCENARIO, DEMO_SCENARIOS
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
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(243,186,47,.25);}
    .sentinel-hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(243,186,47,.45);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(243,186,47,.14), rgba(255,255,255,.02));
        margin-bottom: 1rem;
    }
    .sentinel-kicker {color:#F3BA2F;font-weight:700;letter-spacing:.08em;font-size:.82rem;}
    .sentinel-title {font-size:2.55rem;font-weight:800;line-height:1.05;margin:.25rem 0 .5rem 0;}
    .sentinel-sub {font-size:1.02rem;opacity:.8;max-width:850px;}
    .pill {display:inline-block;padding:.28rem .6rem;border-radius:999px;border:1px solid rgba(243,186,47,.45);margin:.18rem .25rem .18rem 0;font-size:.82rem;}
    div[data-testid="stMetric"] {border:1px solid rgba(255,255,255,.08);padding:.9rem;border-radius:14px;background:rgba(255,255,255,.02);}
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


@st.cache_data(ttl=30)
def get_market_snapshot() -> dict:
    return fetch_market_snapshot(TRACKED_ASSETS)


def load_demo(name: str) -> None:
    scenario = DEMO_SCENARIOS[name]
    st.session_state["max_single_asset_pct"] = scenario["max_single_asset_pct"]
    st.session_state["min_stablecoin_pct"] = scenario["min_stablecoin_pct"]
    for asset, value in scenario["portfolio"].items():
        st.session_state[f"portfolio_{asset}"] = float(value)
    st.session_state["active_demo"] = name
    st.session_state["approval_decision"] = None
    st.session_state["approved_portfolio"] = None


if "max_single_asset_pct" not in st.session_state:
    st.session_state["max_single_asset_pct"] = 40
if "min_stablecoin_pct" not in st.session_state:
    st.session_state["min_stablecoin_pct"] = 15
if "active_demo" not in st.session_state:
    st.session_state["active_demo"] = "Custom"
for asset, value in SAMPLE_PORTFOLIO.items():
    st.session_state.setdefault(f"portfolio_{asset}", float(value))

st.markdown(
    """
    <div class="sentinel-hero">
      <div class="sentinel-kicker">BINANCE AGENT OS · TRACK A</div>
      <div class="sentinel-title">🛡️ Binance Sentinel</div>
      <div class="sentinel-sub">A safety-first portfolio risk agent that combines live Binance market data, user-defined guardrails, explainable risk reasoning, stress testing, simulated rebalancing, and human approval.</div>
      <div style="margin-top:.8rem">
        <span class="pill">Public market data</span>
        <span class="pill">Risk Constitution</span>
        <span class="pill">Explainable agent</span>
        <span class="pill">What-if simulation</span>
        <span class="pill">Human-in-the-loop</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Competition build · no Binance account login · no API key · no live trading")

with st.sidebar:
    st.header("Demo Control")
    scenario_name = st.selectbox("Scenario", list(DEMO_SCENARIOS), index=0)
    st.caption(DEMO_SCENARIOS[scenario_name]["description"])
    if st.button("Load demo scenario", type="primary", use_container_width=True):
        load_demo(scenario_name)
        st.rerun()

    st.caption(f"Active: {st.session_state['active_demo']}")
    st.divider()

    st.header("Risk Constitution")
    st.slider(
        "Maximum single-asset allocation",
        min_value=5,
        max_value=90,
        step=1,
        key="max_single_asset_pct",
    )
    st.slider(
        "Minimum stablecoin allocation",
        min_value=0,
        max_value=90,
        step=1,
        key="min_stablecoin_pct",
    )

    st.divider()
    st.header("Portfolio")
    st.caption("USD values are local demo inputs; no account connection is required.")
    portfolio = {}
    for asset in SAMPLE_PORTFOLIO:
        portfolio[asset] = st.number_input(
            f"{asset} value (USD)",
            min_value=0.0,
            step=10.0,
            key=f"portfolio_{asset}",
        )

constitution = RiskConstitution(
    max_single_asset=st.session_state["max_single_asset_pct"] / 100,
    min_stablecoin=st.session_state["min_stablecoin_pct"] / 100,
)

weights = allocations(portfolio)
total = sum(portfolio.values())
constitution_risk = risk_summary(portfolio, constitution)
proposal = rebalance_proposal(portfolio, constitution)
agent_os_status = skills_hub_status()

if st.button("Refresh live Binance data"):
    st.cache_data.clear()

market_snapshot = get_market_snapshot()
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
action_request = build_action_request(portfolio, proposal, preview)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Portfolio", money(total))
m2.metric("Risk level", market_risk["level"])
m3.metric("Risk score", f"{market_risk['score']:.1f}/100")
m4.metric("24h weighted move", f"{market_risk['weighted_24h_change']:.2f}%")
m5.metric("Action priority", assessment["priority"])

overview_tab, agent_tab, simulation_tab, architecture_tab = st.tabs(
    ["Overview", "Agent Explanation", "Simulation & Approval", "Architecture"]
)

with overview_tab:
    st.subheader("Live Binance Market")
    market_columns = st.columns(len(TRACKED_ASSETS))
    for column, asset in zip(market_columns, TRACKED_ASSETS):
        result = market_snapshot[asset]
        with column:
            if result["ok"]:
                data = result["data"]
                st.metric(
                    f"{asset}/USDT",
                    money(data["price"]),
                    f"{data['change_percent']:.2f}% 24h",
                )
                st.caption(f"High {money(data['high'])} · Low {money(data['low'])}")
                st.caption(data.get("source", "Binance public data"))
            else:
                st.error(f"{asset} data unavailable")

    left, right = st.columns([1.2, 1])
    with left:
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
        st.bar_chart({asset: weight * 100 for asset, weight in weights.items()})

    with right:
        st.subheader("Risk Constitution")
        st.write(
            f"Single-asset ceiling: **{pct(constitution.max_single_asset)}**  \n"
            f"Minimum stablecoin reserve: **{pct(constitution.min_stablecoin)}**"
        )
        st.write(
            f"Current stablecoin allocation: **{pct(constitution_risk['stablecoin_allocation'])}**"
        )
        if constitution_risk["violations"]:
            st.error("Constitution violation detected")
            for violation in constitution_risk["violations"]:
                st.write(
                    f"- {violation['asset']}: {pct(violation['allocation'])} > {pct(violation['limit'])}"
                )
        else:
            st.success("No concentration-limit violations")

        st.subheader("Stress Tests")
        st.dataframe(
            [
                {
                    "Scenario": item["name"],
                    "After": money(item["after"]),
                    "Impact": pct(item["drawdown"]),
                }
                for item in stress_results
            ],
            width="stretch",
            hide_index=True,
        )

    st.subheader("Agent OS Integration")
    i1, i2, i3 = st.columns(3)
    i1.metric("Mode", agent_os_status["mode"])
    i2.metric("Official Binance Skill", "Installed" if agent_os_status["skill_installed"] else "Not detected")
    i3.metric("binance-cli", "Detected" if agent_os_status["active"] else "Optional / inactive")
    st.caption("Sentinel remains operational with public Binance REST market data when the local CLI is unavailable.")

with agent_tab:
    st.subheader("Agent Explanation Panel")
    st.markdown(f"### {assessment['headline']}")

    e1, e2, e3 = st.columns(3)
    e1.metric("Decision priority", assessment["priority"])
    e2.metric("Market-aware score", f"{market_risk['score']:.1f}/100")
    e3.metric("Market data coverage", pct(market_risk["market_data_coverage"]))

    st.write("**Why this score**")
    for reason in market_risk["reasons"]:
        st.write(f"- {reason}")

    observe_col, reason_col = st.columns(2)
    with observe_col:
        st.markdown("#### 1 · Observe")
        for item in assessment["observations"]:
            st.write(f"- {item}")
    with reason_col:
        st.markdown("#### 2 · Reason")
        for item in assessment["reasoning"]:
            st.write(f"- {item}")

    plan_col, guard_col = st.columns(2)
    with plan_col:
        st.markdown("#### 3 · Plan")
        for item in assessment["plan"]:
            st.write(f"- {item}")
    with guard_col:
        st.markdown("#### 4 · Guardrails")
        for item in assessment["guardrails"]:
            st.write(f"- {item}")

    st.info(
        "The reasoning layer explains deterministic risk evidence. It cannot override the Risk Constitution and it cannot execute a trade."
    )

with simulation_tab:
    st.subheader("What-If Rebalance")
    st.caption("Sentinel tests the proposed action before asking a human to approve it.")

    if proposal:
        st.write(
            f"Proposed simulation: move approximately **{money(proposal['reduce_by'])}** "
            f"from **{proposal['asset']}** to **{proposal['destination']}**."
        )

        s1, s2, s3 = st.columns(3)
        s1.metric("Before risk", f"{preview['before_market']['score']:.1f}/100", preview["before_market"]["level"])
        s2.metric("After risk", f"{preview['after_market']['score']:.1f}/100", preview["after_market"]["level"])
        s3.metric("Score change", f"{preview['score_change']:+.1f}")

        if preview["score_change"] < 0 or preview["violations_change"] < 0:
            st.success(preview["verdict"])
        elif preview["score_change"] > 0 or preview["violations_change"] > 0:
            st.error(preview["verdict"])
        else:
            st.info(preview["verdict"])

        st.dataframe(
            [
                {
                    "Asset": row["asset"],
                    "Before": pct(row["before_allocation"]),
                    "After": pct(row["after_allocation"]),
                    "Before value": money(row["before_value"]),
                    "After value": money(row["after_value"]),
                }
                for row in preview["allocation_changes"]
            ],
            width="stretch",
            hide_index=True,
        )

        st.markdown("#### Human Approval Gate")
        if action_request:
            current_action_id = action_request["id"]
            if st.session_state.get("approval_action_id") != current_action_id:
                st.session_state["approval_action_id"] = current_action_id
                st.session_state["approval_decision"] = None
                st.session_state["approved_portfolio"] = None

            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Action ID", action_request["id"])
            a2.metric("From", action_request["source_asset"])
            a3.metric("To", action_request["destination_asset"])
            a4.metric("Amount", money(action_request["amount_usd"]))

            approve_col, reject_col = st.columns(2)
            with approve_col:
                if st.button("Approve simulation", type="primary", use_container_width=True):
                    st.session_state["approval_decision"] = decision_record(action_request, "APPROVED")
                    st.session_state["approved_portfolio"] = action_request["simulated_after_portfolio"]
            with reject_col:
                if st.button("Reject proposal", use_container_width=True):
                    st.session_state["approval_decision"] = decision_record(action_request, "REJECTED")
                    st.session_state["approved_portfolio"] = None

            decision = st.session_state.get("approval_decision")
            if decision:
                if decision["status"] == "APPROVED":
                    st.success(f"Action {decision['id']} approved for local simulation only. No Binance order was sent.")
                else:
                    st.warning(f"Action {decision['id']} rejected. No portfolio state changed.")
    else:
        st.success("No concentration-driven rebalance is required under the current Risk Constitution.")

with architecture_tab:
    st.subheader("System Architecture")
    st.markdown(
        """
```mermaid
flowchart LR
    A[Binance Market Data] --> B[Portfolio + Risk Constitution]
    B --> C[Risk Engine]
    C --> D[Agent Explanation]
    C --> E[Stress Tests]
    D --> F[Rebalance Proposal]
    E --> F
    F --> G[What-If Simulation]
    G --> H{Human Approval}
    H -->|Approve| I[Local Approved State]
    H -->|Reject| J[No Change]
```
        """
    )
    st.caption("Full architecture documentation is available in `docs/ARCHITECTURE.md`.")
    st.warning("Competition safety boundary: execution stops at local human-approved simulation. Live trading is intentionally disabled.")

st.divider()
st.caption(
    "Binance Sentinel · Track A competition build · public market data + deterministic safety rules + explainable reasoning + human-in-the-loop simulation"
)
