"""Curated demo scenarios for the Binance Sentinel competition dashboard."""

DEMO_SCENARIOS = {
    "Competition demo — concentrated risk": {
        "description": (
            "A BTC-heavy portfolio with too little stablecoin reserve. "
            "Designed to trigger Sentinel's full detect → explain → simulate → approve workflow."
        ),
        "portfolio": {
            "BTC": 700.0,
            "ETH": 180.0,
            "BNB": 70.0,
            "USDC": 50.0,
        },
        "max_single_asset_pct": 35,
        "min_stablecoin_pct": 20,
    },
    "Balanced portfolio": {
        "description": (
            "A more diversified portfolio used to show how Sentinel behaves when "
            "the Risk Constitution is mostly satisfied."
        ),
        "portfolio": {
            "BTC": 350.0,
            "ETH": 250.0,
            "BNB": 150.0,
            "USDC": 250.0,
        },
        "max_single_asset_pct": 40,
        "min_stablecoin_pct": 15,
    },
    "Defensive portfolio": {
        "description": (
            "A high-stablecoin portfolio used to demonstrate a lower-risk posture "
            "under the same live market conditions."
        ),
        "portfolio": {
            "BTC": 250.0,
            "ETH": 200.0,
            "BNB": 100.0,
            "USDC": 450.0,
        },
        "max_single_asset_pct": 40,
        "min_stablecoin_pct": 30,
    },
}

DEFAULT_DEMO_SCENARIO = "Competition demo — concentrated risk"
