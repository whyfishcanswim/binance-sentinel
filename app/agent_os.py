"""Binance Agent OS / Skills Hub integration helpers for Sentinel v0.10.

Sentinel can detect the official Binance `binance` Skill installed into the
project and can use `binance-cli` when that executable is available. On Windows,
the Skill may be installed even when the CLI is not yet available; in that case
Sentinel keeps using the public Binance REST fallback while honestly reporting
the integration state.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


BINANCE_SKILLS_REPO = "https://github.com/binance/binance-skills-hub"
BINANCE_SKILL_URL = (
    "https://github.com/binance/binance-skills-hub/tree/main/skills/binance/binance"
)


def _candidate_skill_paths() -> list[Path]:
    cwd = Path.cwd()
    home = Path.home()
    relative_paths = [
        Path(".agents/skills/binance"),
        Path(".codex/skills/binance"),
        Path(".claude/skills/binance"),
        Path(".gemini/skills/binance"),
        Path("skills/binance"),
    ]
    return [cwd / path for path in relative_paths] + [home / path for path in relative_paths]


def skills_hub_status() -> dict:
    """Describe the local official Binance Skill and CLI state."""

    cli_path = shutil.which("binance-cli")
    installed_skill_path = next(
        (path for path in _candidate_skill_paths() if (path / "SKILL.md").exists()),
        None,
    )

    cli_version = None
    cli_error = None

    if cli_path:
        try:
            result = subprocess.run(
                [cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            version_text = (result.stdout or result.stderr).strip()
            cli_version = version_text or "installed"
        except (OSError, subprocess.SubprocessError) as exc:
            cli_error = str(exc)

    skill_installed = installed_skill_path is not None
    cli_active = cli_path is not None

    if skill_installed and cli_active:
        mode = "BINANCE SKILLS + CLI"
    elif skill_installed:
        mode = "BINANCE SKILL INSTALLED"
    else:
        mode = "PUBLIC REST FALLBACK"

    return {
        "active": cli_active,
        "cli_active": cli_active,
        "skill_installed": skill_installed,
        "cli_path": cli_path,
        "cli_version": cli_version,
        "cli_error": cli_error,
        "skill_path": str(installed_skill_path) if installed_skill_path else None,
        "skills_repo": BINANCE_SKILLS_REPO,
        "skill_url": BINANCE_SKILL_URL,
        "mode": mode,
    }


def _parse_json_output(text: str) -> dict:
    """Parse JSON even if the CLI prints a small prefix before the payload."""

    stripped = text.strip()
    if not stripped:
        raise ValueError("binance-cli returned empty output")

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        starts = [index for index in (stripped.find("{"), stripped.find("[")) if index >= 0]
        if not starts:
            raise ValueError("binance-cli output did not contain JSON")
        data = json.loads(stripped[min(starts):])

    if isinstance(data, list):
        if not data:
            raise ValueError("binance-cli returned an empty JSON list")
        data = data[0]

    if not isinstance(data, dict):
        raise ValueError("binance-cli returned an unexpected JSON payload")

    return data


def fetch_spot_24h_via_skill(asset: str) -> dict:
    """Fetch a public Spot 24h ticker through the official Binance CLI.

    The official Binance `binance` Skill documents the public Spot market-data
    command used here. No Binance API credentials are needed for this market
    endpoint.
    """

    cli_path = shutil.which("binance-cli")
    if not cli_path:
        raise FileNotFoundError("binance-cli is not installed or not on PATH")

    symbol = f"{asset.upper()}USDT"
    result = subprocess.run(
        [cli_path, "spot", "ticker24hr", "--symbol", symbol],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(details or f"binance-cli exited with code {result.returncode}")

    data = _parse_json_output(result.stdout)

    return {
        "asset": asset.upper(),
        "symbol": symbol,
        "price": float(data["lastPrice"]),
        "change_percent": float(data["priceChangePercent"]),
        "high": float(data["highPrice"]),
        "low": float(data["lowPrice"]),
        "volume": float(data["volume"]),
        "source": "Binance Agent OS Skills Hub / binance-cli",
    }
