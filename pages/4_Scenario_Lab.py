import streamlit as st

from app.scenario_simulator import SCENARIOS, simulate_scenario

st.set_page_config(page_title="Sentinel Scenario Lab", page_icon="🔮", layout="wide")

st.title("🔮 Sentinel Scenario Lab")
st.caption("Explore possible futures before making portfolio decisions. All scenarios are simulations only.")

scenario_name = st.selectbox("Choose a scenario", list(SCENARIOS.keys()))
scenario = SCENARIOS[scenario_name]

st.info(scenario["description"])

portfolio_value = st.number_input(
    "Current portfolio value (USD)",
    min_value=100.0,
    value=10000.0,
    step=500.0,
)

result = simulate_scenario(portfolio_value, scenario)

c1, c2, c3 = st.columns(3)
c1.metric("Before", f"${result['before']:,.2f}")
c2.metric("After simulation", f"${result['after']:,.2f}")
c3.metric("Impact", f"{result['impact']:.1f}%")

st.subheader("Sentinel Analysis")
for item in result["analysis"]:
    st.write(f"- {item}")

st.warning("This is a what-if simulation. Sentinel does not execute trades or modify any account.")
