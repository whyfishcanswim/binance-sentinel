# Binance Sentinel Architecture

```mermaid
flowchart TD
    A[Binance public market data] --> B[Market Data Adapter]
    S[Official Binance Skill installed] --> B
    B --> C[Portfolio Snapshot]
    C --> D[Risk Constitution]
    D --> E[Deterministic Risk Engine]
    B --> E
    E --> F[Market-Aware Risk Score]
    F --> G[Agent Explanation Layer]
    C --> H[Stress Test Engine]
    E --> I[Rebalance Proposal]
    I --> J[What-If Simulation]
    H --> J
    J --> K[Before vs After Risk]
    K --> L{Human Approval}
    L -->|Approve| M[Approved Local Simulation State]
    L -->|Reject| N[No Change]

    classDef safe fill:#f3ba2f,color:#111,stroke:#111,stroke-width:1px;
    classDef guard fill:#202630,color:#fff,stroke:#f3ba2f,stroke-width:1px;
    classDef data fill:#111827,color:#fff,stroke:#6b7280,stroke-width:1px;

    class D,L safe;
    class E,F,G,H,I,J,K guard;
    class A,S,B,C,M,N data;
```

## Safety boundary

Sentinel v0.10 does not authenticate to a Binance account and does not place real orders. The current execution boundary ends at **human-approved local simulation**.

## Agent loop

1. **Observe** — read public Binance market data and portfolio inputs.
2. **Check** — apply the user's Risk Constitution.
3. **Reason** — explain why risk is elevated or acceptable.
4. **Simulate** — preview a rebalance and rerun risk/stress checks.
5. **Approve** — require an explicit human decision.
6. **Stop** — no live execution is enabled in the competition prototype.
