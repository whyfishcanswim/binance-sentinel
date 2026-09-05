"""User-defined safety rules for Binance Sentinel v0.3."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConstitution:
    """Portfolio limits that Sentinel must respect."""

    max_single_asset: float = 0.40
    min_stablecoin: float = 0.15
    destination_stablecoin: str = "USDC"


def _read_percentage(prompt: str, default: float) -> float:
    """Read a percentage from 0 to 100, using a default when left blank."""

    while True:
        raw = input(f"{prompt} [{default * 100:.0f}%]: ").strip()

        if raw == "":
            return default

        try:
            value = float(raw)
        except ValueError:
            print("Please enter a number such as 40 or 15.")
            continue

        if not 0 < value < 100:
            print("Please enter a percentage greater than 0 and less than 100.")
            continue

        return value / 100


def ask_for_constitution() -> RiskConstitution:
    """Ask the user for portfolio safety limits."""

    print("RISK CONSTITUTION")
    print("-----------------")
    print("Choose your safety rules, or press Enter to keep the defaults.\n")

    max_single_asset = _read_percentage(
        "Maximum allowed allocation for one non-stablecoin asset",
        0.40,
    )
    min_stablecoin = _read_percentage(
        "Minimum stablecoin allocation",
        0.15,
    )

    return RiskConstitution(
        max_single_asset=max_single_asset,
        min_stablecoin=min_stablecoin,
    )
