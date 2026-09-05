"""Sample portfolio and stress scenarios used before Binance authentication is enabled."""

SAMPLE_PORTFOLIO = {
    "BTC": 620.0,
    "ETH": 230.0,
    "BNB": 140.0,
    "USDC": 110.0,
}

STRESS_SCENARIOS = {
    "Moderate selloff": {
        "BTC": -0.05,
        "ETH": -0.07,
        "BNB": -0.06,
        "USDC": 0.00,
    },
    "Severe crypto drawdown": {
        "BTC": -0.12,
        "ETH": -0.18,
        "BNB": -0.15,
        "USDC": 0.00,
    },
}
