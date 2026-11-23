#!/usr/bin/env python3

import base64, json, os, re, sys, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "starter", "kit")
PASS, TOTAL = [], 5
def read(p):
    try: return open(p, encoding="utf-8").read()
    except OSError: return None
def env(key, default):
    for line in (read(os.path.join(KIT, ".env")) or "").splitlines():
        if line.startswith(key + "="): return line.split("=", 1)[1].strip()
    return default
def get(url, auth=None, data=None, timeout=10):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    if auth: req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    return json.load(urllib.request.urlopen(req, timeout=timeout))
def prom(q, base="http://localhost:9090"):
    return get(base + "/api/v1/query?" + urllib.parse.urlencode({"query": q}))["data"]["result"]
def rule(n, ok, title, why):
    print(("  [PASS] " if ok else "  [FAIL] ") + f"Rule {n}: {title}" + ("" if ok else f"  ->  {why}"))
    if ok: PASS.append(n)
def done():
    sc = len(PASS) * 100 // TOTAL
    print("---------------------------------------------------")
    print(f" Test Summary: {len(PASS)} / {TOTAL} checks passed ({sc}%)")
    print("---------------------------------------------------")
    print(" [SUCCESS] All validation checks passed successfully!" if len(PASS) == TOTAL else " [INCOMPLETE] Please address failed checks and re-run.")
    sys.exit(0 if len(PASS) == TOTAL else 1)
def header(t):
    print("==================================================="); print(f" Validating Solution for {t}"); print("===================================================")
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D4_3.json")

GF = "http://localhost:3000"; GAUTH = "admin:" + env("GRAFANA_PASSWORD", "admin")
def import_dashboard(path):
    d = json.load(open(path))
    r = get(GF + "/api/dashboards/db", GAUTH, json.dumps({"dashboard": d, "overwrite": True, "folderId": 0}).encode())
    print("dashboard imported:", r.get("url", r))
def dashboard(uid):
    return get(GF + "/api/dashboards/uid/" + uid, GAUTH)["dashboard"]
def evidence():
    try: return json.loads(read(EVID))
    except Exception: return None
def gv(ev, *k):
    x = ev
    for i in k: x = x.get(i, "") if isinstance(x, dict) else ""
    return x if isinstance(x, str) else ""

if len(sys.argv) > 1 and sys.argv[1] == "import":
    import_dashboard(os.path.join(KIT, "dashboard_sre_broken.json")); sys.exit(0)
header("TEL-D4-403")
try: d = dashboard("shopnow-sre"); gerr = ""
except Exception as e: d, gerr = None, str(e)
panels = {p.get("title"): p for p in (d or {}).get("panels", [])}
lat, err = panels.get("P95 Latency"), panels.get("Service Error Rate")
le = lat["targets"][0]["expr"] if lat else ""; ee = err["targets"][0]["expr"] if err else ""
n = lambda s: s.replace(" ", "").replace("'", '"')
print("      latency: " + le); print("      error  : " + ee)
rule(1, "rate(http_request_duration_seconds_bucket" in n(le) and "sum(" in n(le) and re.search(r"by\(le(,|\))", n(le)) is not None and 'service=~"$service"' in n(le),
     "p95: histogram_quantile(0.95, sum(rate(..._bucket{service=~\"$service\"}[...])) by (le, ...))",
     gerr or "edit panel 'P95 Latency': rate() over the buckets, sum by (le, ...), filter on $service; then SAVE the dashboard")
rule(2, "rate(http_requests_total" in n(ee) and 'status=~"5.."' in n(ee) and "/" in ee and re.search(r"\*100|100\*", n(ee)) is not None and 'service=~"$service"' in n(ee),
     "Error rate: 5xx request rate / total request rate * 100, filtered by $service",
     "edit panel 'Service Error Rate': a percentage = rate of 5xx divided by rate of all requests, times 100")
v = [x for x in (d or {}).get("templating", {}).get("list", []) if x.get("name") == "service"]
rx = v[0].get("regex", "") if v else None
print("      variable regex: %r" % rx)
try: names = get("http://localhost:9090/api/v1/label/service/values")["data"]
except Exception: names = []
pat = (rx or "").strip("/"); shown = []
for s in names:
    m = re.search(pat, s) if pat else None
    if not pat: shown.append(s)
    elif m: shown.append(m.group(1) if m.groups() and m.group(1) is not None else s)   # Grafana uses the first capture group as the value
rule(3, bool(v) and all(s in shown for s in ["order-service", "payment-service", "inventory-api", "notification-service"]),
     "Service variable offers all 4 full service names: %s" % shown,
     "the regex captures only part of the name; use a non-capturing group (?:...) or no group, then save the dashboard")
ok4 = False; why4 = ""
try:
    r1 = prom(n(le).replace("$service", ".*").replace("$__rate_interval", "5m"))
    r2 = prom(n(ee).replace("$service", ".*").replace("$__rate_interval", "5m"))
    v1 = [float(x["value"][1]) for x in r1 if x["value"][1] != "NaN"]; v2 = [float(x["value"][1]) for x in r2 if x["value"][1] != "NaN"]
    ok4 = bool(v1) and all(0 < x < 15 for x in v1) and bool(v2) and all(0 <= x <= 30 for x in v2)
    why4 = f"p95 values {[round(x,2) for x in v1][:4]}, error % {[round(x,2) for x in v2][:4]}"
except Exception as ex: why4 = str(ex)
rule(4, ok4, "Live: both repaired queries evaluate to sane values on Prometheus (p95 0-15 s, error rate 0-30 %)", why4)
ev = evidence(); fix, sec = gv(ev, "telemetryFixes", "primaryQueryOrFix"), gv(ev, "telemetryFixes", "secondaryQueryOrThreshold")
rule(5, bool(ev) and "<<" not in (read(EVID) or "<<") and "histogram_quantile" in fix and "rate(" in fix and re.search(r"\(\?:|non-capturing|capture", sec) is not None
     and gv(ev, "verification", "verifiedOnPlatform").strip().lower() in ("true", "yes") and len(gv(ev, "verification", "mitigationRecommendation")) >= 20,
     "Evidence complete: fixed p95 query, regex fix (non-capturing group), verifiedOnPlatform = true, recommendation",
     "evidence_D4_3.json: primaryQueryOrFix = the p95 query; secondaryQueryOrThreshold = the regex fix; no <<FILL_...>> left")
done()
