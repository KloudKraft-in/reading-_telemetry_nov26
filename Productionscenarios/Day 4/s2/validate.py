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
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D4_2.json")

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

sub = lambda e: e.replace("$__rate_interval", "5m").replace("$__interval", "1m").replace("$__range", "5m")
if len(sys.argv) > 1 and sys.argv[1] == "import":
    import_dashboard(os.path.join(KIT, "dashboard_broken.json")); sys.exit(0)
header("TEL-D4-402")
try: d = dashboard("payment-dashboard"); gerr = ""
except Exception as e: d, gerr = None, str(e)
p = [x for x in (d or {}).get("panels", []) if x.get("title") == "Payment Error Volume"]
e = (p[0]["targets"][0].get("expr", "") if p else ""); en = e.replace(" ", "")
print("      expr: " + e)
rule(1, bool(p) and '|="error"' not in en and "|='error'" not in en and "|json" in en and ('level="ERROR"' in en or 'level=~"(?i)error"' in en) and ("rate(" in en or "count_over_time(" in en),
     "Panel query repaired: no naive |= \"error\", uses | json, level = \"ERROR\", rate()/count_over_time()",
     gerr or "open Grafana -> Payment Dashboard -> panel 'Payment Error Volume' -> edit the query, then SAVE the dashboard")
val = None; lerr = ""
try:
    r = get("http://localhost:3100/loki/api/v1/query?" + urllib.parse.urlencode({"query": sub(e)}))["data"]["result"]
    val = float(r[0]["value"][1]) if r else 0.0
except Exception as ex: lerr = str(ex)
rule(2, val is not None and val >= 20, "Live: repaired query shows >= 20 errors per minute during the outage" + (f" (value={val:.1f})" if val is not None else ""),
     "the query must return an errors-per-minute number (count_over_time(...[1m]) or rate(...)*60); is the outage on and 5 minutes old?  " + (lerr or "value too low"))
steps = ((p[0].get("fieldConfig", {}).get("defaults", {}).get("thresholds", {}).get("steps", [])) if p else [])
vals = sorted(s["value"] for s in steps if s.get("value") is not None)
cols = [s.get("color", "") for s in sorted(steps, key=lambda s: -1 if s.get("value") is None else s["value"])]
print("      thresholds: " + str([(s.get("color"), s.get("value")) for s in steps]))
rule(3, vals == [5, 20] and bool(cols) and "green" in cols[0] and "red" in cols[-1], "Thresholds: green below 5, warning (yellow/orange) from 5, red (critical) from 20 errors per minute",
     "set steps: base green, 5 = yellow, 20 = red, then save the dashboard")
ev = evidence(); sec = gv(ev, "telemetryFixes", "secondaryQueryOrThreshold")
rule(4, bool(ev) and "level" in gv(ev, "telemetryFixes", "primaryQueryOrFix") and "json" in gv(ev, "telemetryFixes", "primaryQueryOrFix").lower()
     and re.search(r"case|upper|json|structured|line filter", (gv(ev, "incidentSummary", "rootCauseComponent") + gv(ev, "incidentSummary", "observedDefect")).lower()) is not None
     and "5" in sec and "20" in sec,
     "Evidence: fixed query (json, level), why the old one returned 0 (case / JSON / line filter), thresholds 5 and 20",
     "evidence_D4_2.json: fill primaryQueryOrFix, explain the cause in incidentSummary, name the thresholds in secondaryQueryOrThreshold")
rule(5, bool(ev) and "<<" not in (read(EVID) or "<<") and gv(ev, "verification", "verifiedOnPlatform").strip().lower() in ("true", "yes") and len(gv(ev, "verification", "mitigationRecommendation")) >= 20,
     "Evidence complete: no placeholders, verifiedOnPlatform = true, mitigation recommendation given",
     "replace every <<FILL_...>> value; verifiedOnPlatform must be true once the live panel shows errors")
done()
