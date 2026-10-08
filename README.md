# dsco-exec

TWAP, VWAP and optimal (Almgren-Chriss) execution schedules, plus execution-quality reports, from [distributed.systems](https://distributed.systems). Zero dependencies.

```sh
pip install dsco-exec
export DSCO_API_KEY=sk-dsco-...
dsco-exec twap buy 10000 2026-10-08T13:30:00Z 2026-10-08T20:00:00Z --slices 26
```

```python
from dsco_exec import Client

ex = Client()
plan = ex.vwap("sell", 50_000, "2026-10-08T13:30:00Z", "2026-10-08T20:00:00Z",
               expected_total_volume=2_000_000, max_participation=0.1, lot_size=100)
for child in plan["children"]:
    print(child["time"], child["quantity"])

ac = ex.almgren_chriss("buy", 100_000, "2026-10-08T13:30:00Z", "2026-10-08T20:00:00Z",
                       volatility=0.35, temporary_impact=2e-6, risk_aversion=1e-6)
print(ac["expected_cost"], ac["cost_variance"])

quality = ex.report("buy", fills=[{"price": 101.2, "quantity": 600}, {"price": 101.5, "quantity": 400}],
                    arrival_price=101.0, market_vwap=101.3)
print(quality["implementation_shortfall_bps"], quality["vs_vwap_bps"])
```

More: `ex.pov(...)` percentage-of-volume, `ex.replan(...)` adaptive catch-up from live fills,
`ex.impact(...)` square-root pre-trade cost and the horizon for a cost budget. Every schedule accepts
`randomize=0.2, seed=42` (anti-gaming jitter), `reference_price=..., aggression_bps=...` (child limits),
and VWAP takes `profile="crypto_24h"` with `buckets=96`.

Schedules are advice: you place child orders with your own broker. Nothing here holds funds or routes orders.
