#!/usr/bin/env python3
"""Day 5 Lab 4 — writes two Grafana dashboards as API payloads:
  golden-signals.json  "Shop — Golden Signals" (L3, one selected service; the Saturation row is left for you to build)
  executive.json       "Shop — Executive Summary" (L1, business view of the whole shop for the selected time range)"""
import json

DS = {"type": "prometheus", "uid": "prometheus"}
SEL = 'env="$env",service="$service",route=~"$route"'
REQ, BKT = "http_server_requests_total", "http_server_request_duration_seconds_bucket"

def thresholds(*steps):
    return {"mode": "absolute", "steps": [{"color": c, "value": v} for c, v in steps]}
def panel(pid, kind, title, desc, x, y, w, h, exprs, unit, th=None, legend=None, extra=None):
    p = {"id": pid, "type": kind, "title": title, "description": desc, "datasource": DS,
         "gridPos": {"x": x, "y": y, "w": w, "h": h},
         "targets": [{"refId": chr(65 + i), "datasource": DS, "expr": e, "legendFormat": (legend or ["__auto"] * 9)[i]} for i, e in enumerate(exprs)],
         "fieldConfig": {"defaults": {"unit": unit}, "overrides": []}, "options": {}}
    if th: p["fieldConfig"]["defaults"]["thresholds"] = th
    if kind == "stat": p["options"] = {"colorMode": "background", "graphMode": "area", "reduceOptions": {"calcs": ["lastNotNull"]}}
    if kind == "timeseries" and th: p["fieldConfig"]["defaults"]["custom"] = {"thresholdsStyle": {"mode": "line+area"}}
    if extra: p.update(extra)
    return p
def row(pid, title, y):
    return {"id": pid, "type": "row", "title": title, "collapsed": False, "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []}

LAT_TH = thresholds(("green", None), ("orange", 0.5), ("red", 1))
ERR_TH = thresholds(("green", None), ("orange", 0.01), ("red", 0.05))
SAT_TH = thresholds(("green", None), ("orange", 0.7), ("red", 0.9))
P95 = f'histogram_quantile(0.95, sum by (le) (rate({BKT}{{{SEL}}}[$__rate_interval])))'
RPS = f'sum(rate({REQ}{{{SEL}}}[$__rate_interval]))'
ERR = f'(sum(rate({REQ}{{{SEL},status=~"5.."}}[$__rate_interval])) or vector(0)) / {RPS}'

golden = {
    "uid": "shop-golden", "title": "Shop — Golden Signals", "tags": ["shop", "L3-service", "golden-signals"],
    "description": "L3 service view: latency, traffic, errors and saturation of ONE service. Pick the service at the top.",
    "time": {"from": "now-30m", "to": "now"}, "refresh": "30s", "schemaVersion": 41,
    "links": [{"title": "Up: Shop Operations", "type": "dashboards", "tags": ["L2-operations"], "asDropdown": False, "includeVars": True, "keepTime": True},
              {"title": "Runbook: checkout", "type": "link", "url": "http://localhost:9095/runbooks/RB-CHK-002.html", "targetBlank": True}],
    "templating": {"list": [
        {"name": "env", "label": "Environment", "type": "custom", "query": "lab,prod", "current": {"text": "lab", "value": "lab"}},
        {"name": "service", "label": "Service", "type": "query", "datasource": DS, "refresh": 2, "sort": 1,
         "query": {"query": f'label_values({REQ}{{env="$env"}}, service)', "refId": "service"},
         "definition": f'label_values({REQ}{{env="$env"}}, service)', "current": {"text": "checkout", "value": "checkout"}},
        {"name": "route", "label": "Route", "type": "query", "datasource": DS, "refresh": 2, "includeAll": True, "multi": True, "allValue": ".*",
         "query": {"query": f'label_values({REQ}{{env="$env",service="$service"}}, route)', "refId": "route"},
         "definition": f'label_values({REQ}{{env="$env",service="$service"}}, route)', "current": {"text": "All", "value": "$__all"}},
    ]},
    "panels": [
        row(1, "Golden signals — $service (now)", 0),
        panel(2, "stat", "Latency p95", "95 % of requests to $service were faster than this. Orange > 0.5 s, red > 1 s.", 0, 1, 6, 4, [P95], "s", LAT_TH),
        panel(3, "stat", "Traffic", "Requests per second handled by $service.", 6, 1, 6, 4, [RPS], "reqps"),
        panel(4, "stat", "Errors (5xx %)", "Share of requests answered with HTTP 5xx. Orange > 1 %, red > 5 %.", 12, 1, 6, 4, [ERR], "percentunit", ERR_TH),
        panel(5, "text", "Saturation — build me", "Placeholder for the saturation stat (Task 2).", 18, 1, 6, 4, [], "none",
              extra={"options": {"mode": "markdown", "content": "**Task 2:** replace this panel with a *Saturation* stat (CPU of `$service`)."}, "targets": []}),
        row(6, "Latency & traffic — trends", 5),
        panel(7, "timeseries", "Latency p50 / p95 / p99", "Percentiles of request duration. A gap between p50 and p99 means a slow minority.", 0, 6, 12, 8,
              [f'histogram_quantile({q}, sum by (le) (rate({BKT}{{{SEL}}}[$__rate_interval])))' for q in ("0.5", "0.95", "0.99")], "s", LAT_TH, ["p50", "p95", "p99"]),
        panel(8, "timeseries", "Traffic by route", "Requests per second per route of $service.", 12, 6, 12, 8,
              [f'sum by (route) (rate({REQ}{{{SEL}}}[$__rate_interval]))'], "reqps", legend=["{{route}}"]),
        row(9, "Errors — trends", 14),
        panel(10, "timeseries", "Error ratio (5xx)", "Share of 5xx responses over time.", 0, 15, 12, 8, [ERR], "percentunit", ERR_TH, ["5xx ratio"]),
        panel(11, "timeseries", "Non-2xx responses by status", "Which status codes are returned, per second.", 12, 15, 12, 8,
              [f'sum by (status) (rate({REQ}{{{SEL},status!~"2.."}}[$__rate_interval]))'], "reqps", legend=["{{status}}"]),
    ],
}

E = 'env="$env",service="frontend"'
AVAIL = f'1 - (sum(increase({REQ}{{{E},status=~"5.."}}[$__range])) or vector(0)) / sum(increase({REQ}{{{E}}}[$__range]))'
executive = {
    "uid": "shop-exec", "title": "Shop — Executive Summary", "tags": ["shop", "L1-executive"],
    "description": "L1 business view for the time range in the picker. Availability objective: 99.5 % of requests without a server error.",
    "time": {"from": "now-1h", "to": "now"}, "refresh": "1m", "schemaVersion": 41,
    "links": [{"title": "Down: Shop Operations", "type": "dashboards", "tags": ["L2-operations"], "asDropdown": False, "includeVars": True, "keepTime": True}],
    "templating": {"list": [{"name": "env", "label": "Environment", "type": "custom", "query": "lab,prod", "current": {"text": "lab", "value": "lab"}}]},
    "panels": [
        panel(1, "stat", "Availability (objective 99.5 %)", "Share of shop requests without a server error in the selected range.", 0, 0, 6, 5, [AVAIL], "percentunit",
              thresholds(("red", None), ("green", 0.995)), extra={"options": {"colorMode": "background", "graphMode": "none", "reduceOptions": {"calcs": ["lastNotNull"]}}}),
        panel(2, "stat", "Error budget left", "How much of the 0.5 % allowed failures is still unused (100 % = no failures, below 0 = objective missed).", 6, 0, 6, 5,
              [f'1 - (1 - ({AVAIL})) / 0.005'], "percentunit",
              thresholds(("red", None), ("orange", 0.25), ("green", 0.5)), extra={"options": {"colorMode": "background", "graphMode": "none", "reduceOptions": {"calcs": ["lastNotNull"]}}}),
        panel(3, "stat", "Orders completed", "Successful checkouts (HTTP 201) in the selected range.", 12, 0, 6, 5,
              [f'sum(increase({REQ}{{{E},route="/api/checkout",status="201"}}[$__range]))'], "short",
              extra={"options": {"colorMode": "none", "graphMode": "none", "reduceOptions": {"calcs": ["lastNotNull"]}}, "fieldConfig": {"defaults": {"unit": "short", "decimals": 0}, "overrides": []}}),
        panel(4, "stat", "Checkout p95 (target 1 s)", "95 % of checkouts in the selected range were faster than this.", 18, 0, 6, 5,
              [f'histogram_quantile(0.95, sum by (le) (increase({BKT}{{{E},route="/api/checkout"}}[$__range])))'], "s",
              thresholds(("green", None), ("red", 1)), extra={"options": {"colorMode": "background", "graphMode": "none", "reduceOptions": {"calcs": ["lastNotNull"]}}}),
        panel(5, "timeseries", "Orders per minute — completed vs failed", "Completed and failed checkouts per minute.", 0, 5, 16, 8,
              [f'sum(rate({REQ}{{{E},route="/api/checkout",status="201"}}[$__rate_interval])) * 60',
               f'(sum(rate({REQ}{{{E},route="/api/checkout",status=~"5.."}}[$__rate_interval])) or vector(0)) * 60'], "short", legend=["completed", "failed"]),
        panel(6, "text", "How to read this page", "", 16, 5, 8, 8, [], "none", extra={"targets": [], "options": {"mode": "markdown", "content":
              "**Green** = objective met. **Red** = objective missed in the selected range.\n\n"
              "* Availability below 99.5 % or error budget below 0 → ask the operations team for the incident summary.\n"
              "* Follow **Down: Shop Operations** (top right) for details."}}),
    ],
}

for name, d in (("golden-signals.json", golden), ("executive.json", executive)):
    with open(name, "w") as f:
        json.dump({"dashboard": d, "folderUid": "shop-l3" if d["uid"] == "shop-golden" else "shop-l1", "overwrite": True}, f, indent=1)
    print(f"{name}: {d['title']} — {sum(1 for p in d['panels'] if p['type'] != 'row')} panels")
