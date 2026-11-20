#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLO Burn Rate Checker — Queries Prometheus, computes burn rates, alerts on budget exhaustion.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib.request
import urllib.parse


@dataclass
class SLO:
    name: str
    description: str
    sli_query: str  # PromQL for SLI (e.g., "sum(rate(http_requests_total{code!~'5..'}[5m])) / sum(rate(http_requests_total[5m]))")
    target: float  # SLO target (e.g., 0.9995 for 99.95%)
    window: str  # Time window (e.g., "30d", "7d", "1h")
    alert_on_burn_rate: float = 1.0  # Alert if burn rate exceeds this


@dataclass
class BurnRateResult:
    slo_name: str
    sli_value: float
    target: float
    error_budget_remaining: float  # 0-1
    burn_rate: float
    budget_exhaustion_time: Optional[str]  # ISO format or "infinite"
    alert: bool
    window: str
    timestamp: str


class PrometheusClient:
    def __init__(self, url: str, timeout: int = 30):
        self.url = url.rstrip("/")
        self.timeout = timeout

    def query(self, query: str, time: str = None) -> Dict[str, Any]:
        """Execute instant query."""
        params = {"query": query}
        if time:
            params["time"] = time
        url = f"{self.url}/api/v1/query?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode())

    def query_range(self, query: str, start: str, end: str, step: str) -> Dict[str, Any]:
        """Execute range query."""
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step,
        }
        url = f"{self.url}/api/v1/query_range?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode())


def parse_window(window: str) -> timedelta:
    """Parse window string like '30d', '7d', '1h' to timedelta."""
    unit = window[-1]
    value = int(window[:-1])
    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "w":
        return timedelta(weeks=value)
    else:
        raise ValueError(f"Unknown window unit: {unit}")


def calculate_burn_rate(sli_value: float, target: float, window: timedelta) -> float:
    """Calculate burn rate.
    
    Burn rate = (1 - SLI) / (1 - target)
    - 1.0 = consuming budget at expected rate
    - 2.0 = consuming budget 2x faster (will exhaust in half the window)
    - 10.0 = consuming budget 10x faster
    """
    if target >= 1.0:
        return float('inf') if sli_value < 1.0 else 0.0
    if sli_value >= 1.0:
        return 0.0
    
    error_rate = 1.0 - sli_value
    allowed_error_rate = 1.0 - target
    
    if allowed_error_rate <= 0:
        return float('inf')
    
    return error_rate / allowed_error_rate


def estimate_exhaustion(burn_rate: float, window: timedelta, now: datetime) -> Optional[str]:
    """Estimate when budget will be exhausted."""
    if burn_rate <= 0:
        return None
    if burn_rate == float('inf'):
        return now.isoformat()
    
    # Time to exhaust = window / burn_rate
    remaining_fraction = 1.0 / burn_rate if burn_rate > 0 else float('inf')
    if remaining_fraction >= 1.0:
        return None  # Won't exhaust within window
    
    exhaustion_time = now + window * remaining_fraction
    return exhaustion_time.isoformat()


def evaluate_slo(client: PrometheusClient, slo: SLO, now: datetime = None) -> BurnRateResult:
    """Evaluate a single SLO."""
    if now is None:
        now = datetime.utcnow()
    
    window_td = parse_window(slo.window)
    start_time = (now - window_td).isoformat() + "Z"
    end_time = now.isoformat() + "Z"
    
    # Query SLI value over the window
    result = client.query(slo.sli_query)
    
    if result.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {result}")
    
    data = result.get("data", {}).get("result", [])
    if not data:
        raise RuntimeError(f"No data returned for query: {slo.sli_query}")
    
    # Take the first result value
    sli_value = float(data[0]["value"][1])
    
    # Calculate burn rate
    burn_rate = calculate_burn_rate(sli_value, slo.target, window_td)
    
    # Error budget remaining
    error_budget_remaining = max(0.0, 1.0 - (1.0 - sli_value) / (1.0 - slo.target)) if slo.target < 1.0 else 1.0
    
    # Exhaustion estimate
    exhaustion = estimate_exhaustion(burn_rate, window_td, now)
    
    # Alert check
    alert = burn_rate >= slo.alert_on_burn_rate
    
    return BurnRateResult(
        slo_name=slo.name,
        sli_value=sli_value,
        target=slo.target,
        error_budget_remaining=error_budget_remaining,
        burn_rate=burn_rate,
        budget_exhaustion_time=exhaustion,
        alert=alert,
        window=slo.window,
        timestamp=now.isoformat() + "Z"
    )


def load_slos(slo_file: Path) -> List[SLO]:
    """Load SLOs from YAML/JSON file."""
    import yaml
    with open(slo_file) as f:
        if slo_file.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    
    slos = []
    for item in data.get("slos", data if isinstance(data, list) else []):
        slos.append(SLO(
            name=item["name"],
            description=item.get("description", ""),
            sli_query=item["sli_query"],
            target=item["target"],
            window=item.get("window", "30d"),
            alert_on_burn_rate=item.get("alert_on_burn_rate", 1.0)
        ))
    return slos


def main():
    parser = argparse.ArgumentParser(description="Check SLO burn rates from Prometheus")
    parser.add_argument("--prometheus", required=True, help="Prometheus URL (e.g., http://prometheus:9090)")
    parser.add_argument("--slos", required=True, type=Path, help="SLO definitions file (YAML/JSON)")
    parser.add_argument("--window", help="Override window (e.g., 30d, 7d, 1h)")
    parser.add_argument("--format", choices=["json", "text", "prometheus"], default="text", help="Output format")
    parser.add_argument("--output", "-o", type=Path, help="Output file")
    parser.add_argument("--alert-threshold", type=float, default=1.0, help="Alert on burn rate >= threshold")
    args = parser.parse_args()

    client = PrometheusClient(args.prometheus)
    slos = load_slos(args.slos)

    if args.window:
        for slo in slos:
            slo.window = args.window

    results = []
    alerts = []

    for slo in slos:
        try:
            result = evaluate_slo(client, slo)
            results.append(result)
            if result.alert:
                alerts.append(result)
        except Exception as e:
            print(f"❌ Error evaluating {slo.name}: {e}", file=sys.stderr)
            results.append(BurnRateResult(
                slo_name=slo.name,
                sli_value=0.0,
                target=slo.target,
                error_budget_remaining=0.0,
                burn_rate=float('inf'),
                budget_exhaustion_time=datetime.utcnow().isoformat() + "Z",
                alert=True,
                window=slo.window,
                timestamp=datetime.utcnow().isoformat() + "Z"
            ))

    # Output
    if args.format == "json":
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": [asdict(r) for r in results],
            "alerts": [asdict(r) for r in alerts]
        }
        output_str = json.dumps(output, indent=2)
    elif args.format == "prometheus":
        # Prometheus alert format
        lines = []
        for r in results:
            labels = f'slo="{r.slo_name}",target="{r.target}",window="{r.window}"'
            lines.append(f'slo_burn_rate{{{labels}}} {r.burn_rate}')
            lines.append(f'slo_error_budget_remaining{{{labels}}} {r.error_budget_remaining}')
            lines.append(f'slo_alert{{{labels}}} {1 if r.alert else 0}')
        output_str = "\n".join(lines)
    else:
        # Text format
        lines = ["# SLO Burn Rate Report", f"**Time**: {datetime.utcnow().isoformat()}Z", ""]
        for r in results:
            status = "🔴 ALERT" if r.alert else "✅ OK"
            lines.append(f"## {r.slo_name} {status}")
            lines.append(f"- **SLI Value**: {r.sli_value:.6f}")
            lines.append(f"- **Target**: {r.target:.6f} ({r.target*100:.4f}%)")
            lines.append(f"- **Error Budget Remaining**: {r.error_budget_remaining:.2%}")
            lines.append(f"- **Burn Rate**: {r.burn_rate:.2f}x")
            if r.budget_exhaustion_time:
                lines.append(f"- **Budget Exhaustion**: {r.budget_exhaustion_time}")
            else:
                lines.append(f"- **Budget Exhaustion**: Not within window")
            lines.append(f"- **Window**: {r.window}")
            lines.append("")
        output_str = "\n".join(lines)

    if args.output:
        args.output.write_text(output_str, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output_str)

    # Exit code
    if alerts:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()