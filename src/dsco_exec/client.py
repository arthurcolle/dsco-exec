from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_BASE_URL = "https://tools.distributed.systems"
BACKEND = "distributed-execution"


class DscoExecError(RuntimeError):
    """The service rejected the request or returned an error result."""


class Client:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key or os.environ.get("DSCO_API_KEY", "")
        if not self.api_key:
            raise DscoExecError("Set DSCO_API_KEY or pass api_key= (get one at https://distributed.systems)")
        self.base_url = (base_url or os.environ.get("DSCO_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout

    def call(self, tool: str, **arguments: Any) -> Dict[str, Any]:
        body = json.dumps({"tool": f"{BACKEND}:{tool}",
                           "arguments": {k: v for k, v in arguments.items() if v is not None}}).encode()
        request = urllib.request.Request(
            self.base_url + "/api/v1/tools/execute", data=body, method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                     "User-Agent": "dsco-exec/0.1.0"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
        except urllib.error.HTTPError as error:
            detail = error.read()[:500].decode("utf-8", "replace")
            raise DscoExecError(f"HTTP {error.code}: {detail}") from None
        result = payload.get("result") or {}
        if not payload.get("success", True) or result.get("isError"):
            text = payload.get("error") or " ".join(c.get("text", "") for c in result.get("content", []))
            raise DscoExecError(text or "request failed")
        if "structuredContent" in result:
            return result["structuredContent"]
        content = result.get("content") or []
        return json.loads(content[0]["text"]) if content else result

    def twap(self, side: str, quantity: float, start: str, end: str, *, slices: int = 12,
             lot_size: float = 1, min_clip: float = 0) -> Dict[str, Any]:
        return self.call("twap_schedule", side=side, quantity=quantity, start=start, end=end,
                         slices=slices, lot_size=lot_size, min_clip=min_clip)

    def vwap(self, side: str, quantity: float, start: str, end: str, *,
             volume_profile: Optional[Sequence[float]] = None, expected_total_volume: Optional[float] = None,
             max_participation: float = 1.0, lot_size: float = 1, min_clip: float = 0) -> Dict[str, Any]:
        return self.call("vwap_schedule", side=side, quantity=quantity, start=start, end=end,
                         volume_profile=list(volume_profile) if volume_profile else None,
                         expected_total_volume=expected_total_volume, max_participation=max_participation,
                         lot_size=lot_size, min_clip=min_clip)

    def almgren_chriss(self, side: str, quantity: float, start: str, end: str, *, volatility: float,
                       temporary_impact: float, permanent_impact: float = 0, risk_aversion: float = 1e-6,
                       half_spread: float = 0, slices: int = 20, lot_size: float = 1) -> Dict[str, Any]:
        return self.call("almgren_chriss_schedule", side=side, quantity=quantity, start=start, end=end,
                         volatility=volatility, temporary_impact=temporary_impact,
                         permanent_impact=permanent_impact, risk_aversion=risk_aversion,
                         half_spread=half_spread, slices=slices, lot_size=lot_size)

    def report(self, side: str, fills: List[Dict[str, Any]], arrival_price: float, *,
               market_vwap: Optional[float] = None, intended_quantity: Optional[float] = None,
               fees: float = 0) -> Dict[str, Any]:
        return self.call("execution_report", side=side, fills=fills, arrival_price=arrival_price,
                         market_vwap=market_vwap, intended_quantity=intended_quantity, fees=fees)
