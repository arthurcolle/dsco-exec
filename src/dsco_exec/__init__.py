"""TWAP, VWAP and optimal execution schedules from distributed.systems.

    from dsco_exec import Client
    ex = Client()  # reads DSCO_API_KEY
    plan = ex.twap("buy", 10_000, "2026-10-08T13:30:00Z", "2026-10-08T20:00:00Z", slices=26)
    for child in plan["children"]:
        broker.submit(side="buy", qty=child["quantity"], at=child["time"])
"""

from .client import Client, DscoExecError

__all__ = ["Client", "DscoExecError"]
__version__ = "0.1.0"
