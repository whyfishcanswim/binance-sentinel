# Binance Sentinel

**Binance Sentinel** is a hackathon project for Binance Agent OS Track A.

The long-term goal is to build a portfolio-risk agent that can read live Binance data, detect portfolio risk, enforce user-defined safety rules, recommend actions, and eventually execute approved actions through Binance Agent OS.

## Current milestone — v0.1

For the first version, Sentinel does only one thing:

1. Connect to the official Binance Agent OS MCP endpoint.
2. Discover the tools exposed by Binance.
3. Print those tool names in the terminal.

This deliberately avoids trading and account permissions while we verify the basic Agent OS connection.

Official Binance MCP endpoint:

```text
https://agent.binance.com/mcp/agentic
```

## Run locally on Windows

### 1. Install Python

Install Python 3.11 or newer if you do not already have it.

Check it with:

```powershell
python --version
```

### 2. Clone this repository

```powershell
git clone https://github.com/whydidsheleave/binance-sentinel.git
cd binance-sentinel
```

### 3. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Run Sentinel

```powershell
python main.py
```

A successful run should show that Sentinel connected and then print the Binance MCP tools it can discover.

## Planned development

- v0.1 — Connect to Binance MCP and discover tools
- v0.2 — Read real market data
- v0.3 — Add a basic market-risk scan
- v0.4 — Read Agentic sub-account portfolio data
- v0.5 — Calculate portfolio concentration risk
- v0.6 — Add the Risk Constitution
- v0.7 — Add AI reasoning
- v0.8 — Add portfolio stress testing
- v0.9 — Generate rebalancing proposals
- v1.0 — Human-approval-gated execution
- v1.1 — Hackathon dashboard and demo

## Safety design

```text
AI recommendation
      ↓
Risk Constitution
      ↓
Safety validation
      ↓
Human approval
      ↓
Binance action
```

Trading permissions will not be added until the read-only components are working correctly.

## References

- Binance Agent OS announcement: https://www.binance.com/en-IN/support/announcement/detail/07d45cdd3831498f8a4ff339031a8480
- Binance MCP documentation: https://developers.binance.com/en/docs/agent-native/mcp-server/agentic
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
