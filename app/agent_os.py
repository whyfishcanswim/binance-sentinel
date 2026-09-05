"""Binance Agent OS / Skills Hub integration helpers for Sentinel v0.10.

Sentinel detects the official Binance `binance` Skill installed into the
project and can use `binance-cli` either directly or through Windows Subsystem
for Linux (WSL). If neither CLI path is available, Sentinel safely keeps using
public Binance REST market data while reporting that fallback clearly.
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


def _detect_wsl_cli() -> dict | None:
    """Return WSL binance-cli metadata when available."""

    wsl_path = shutil.which("wsl") or shutil.which("wsl.exe")
    if not wsl_path:
        return None

    try:
        probe = subprocess.run(
            [wsl_path, "sh", "-lc", "command -v binance-cli && binance-cli --version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if probe.returncode != 0:
        return None

    lines = [line.strip() for line in probe.stdout.splitlines() if line.strip()]
    if not lines:
        return None

    return {
        "launcher": wsl_path,
        "path": lines[0],
        "version": lines[-1] if len(lines) > 1 else "installed",
    }


def skills_hub_status() -> dict:
    """Describe the local official Binance Skill and CLI state."""

    direct_cli_path = shutil.which("binance-cli")
    wsl_cli = None if direct_cli_path else _detect_wsl_cli()

    installed_skill_path = next(
        (path for path in _candidate_skill_paths() if (path / "SKILL.md").exists()),
        None,
    )

    cli_version = None
    cli_error = None
    cli_transport = None
    cli_path = direct_cli_path

    if direct_cli_path:
        cli_transport = "DIRECT"
        try:
            result = subprocess.run(
                [direct_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            version_text = (result.stdout or result.stderr).strip()
            cli_version = version_text or "installed"
        except (OSError, subprocess.SubprocessError) as exc:
            cli_error = str(exc)
    elif wsl_cli:
        cli_transport = "WSL"
        cli_path = wsl_cli["path"]
        cli_version = wsl_cli["version"]

    skill_installed = installed_skill_path is not None
    cli_active = cli_transport is not None

    if skill_installed and cli_active:
        mode = "BINANCE SKILLS + CLI"
    elif skill_installed:
        mode = "BINANCE SKILL INSTALLED"
    else:
        mode = "PUBLIC REST FALLBACK"

    return {
        "active": cli_active,
        "cli_active": cli_active,
        "cli_transport": cli_transport,
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


def _run_binance_cli(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    """Run binance-cli directly or through WSL."""

    direct_cli_path = shutil.which("binance-cli")
    if direct_cli_path:
        command = [direct_cli_path, *arguments]
    else:
        wsl_cli = _detect_wsl_cli()
        wsl_path = shutil.which("wsl") or shutil.which("wsl.exe")
        if not wsl_cli or not wsl_path:
            raise FileNotFoundError("binance-cli is not installed directly or in WSL")

        shell_command = "binance-cli " + " ".join(
            subprocess.list2cmdline([argument]) for argument in arguments
        )
        command = [wsl_path, "sh", "-lc", shell_command]

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=12,
        check=False,
    )


def fetch_spot_24h_via_skill(asset: str) -> dict:
    """Fetch a public Spot 24h ticker through the official Binance CLI.

    Binance's official Spot skill lists `ticker24hr` under Market endpoints,
    while account and trade endpoints are separately marked as auth-required.
    Sentinel only calls the public market endpoint here.
    """

    symbol = f"{asset.upper()}USDT"
    result = _run_binance_cli(["spot", "ticker24hr", "--symbol", symbol])

    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(details or f"binance-cli exited with code {result.returncode}")

    data = _parse_json_output(result.stdout)
    status = skills_hub_status()
    transport = status.get("cli_transport") or "CLI"

    return {
        "asset": asset.upper(),
        "symbol": symbol,
        "price": float(data["lastPrice"]),
        "change_percent": float(data["priceChangePercent"]),
        "high": float(data["highPrice"]),
        "low": float(data["lowPrice"]),
        "volume": float(data["volume"]),
        "source": f"Binance Agent OS Skills Hub / binance-cli ({transport})",
    }
