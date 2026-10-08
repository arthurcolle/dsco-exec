"""dsco-exec twap|vwap BUY|SELL QTY START END [--slices N] [--lot N] [--json]"""
import argparse
import json
import sys

from .client import Client, DscoExecError


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="dsco-exec", description="Execution schedules from distributed.systems")
    p.add_argument("algorithm", choices=["twap", "vwap"])
    p.add_argument("side", choices=["buy", "sell"])
    p.add_argument("quantity", type=float)
    p.add_argument("start")
    p.add_argument("end")
    p.add_argument("--slices", type=int, default=12)
    p.add_argument("--lot", type=float, default=1)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        ex = Client()
        plan = (ex.twap(a.side, a.quantity, a.start, a.end, slices=a.slices, lot_size=a.lot) if a.algorithm == "twap"
                else ex.vwap(a.side, a.quantity, a.start, a.end, lot_size=a.lot))
    except DscoExecError as error:
        print(f"dsco-exec: {error}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(plan, indent=2))
    else:
        for c in plan["children"]:
            print(f"{c['time']}  {a.side:4}  {c['quantity']:>14g}  (cum {c['cumulative']:g})")
        for note in plan.get("notes", []):
            print(f"note: {note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
