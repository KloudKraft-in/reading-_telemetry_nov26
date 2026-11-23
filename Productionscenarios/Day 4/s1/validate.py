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
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D4_1.md")

def section(txt, n):
    m = re.search(r"^## " + str(n) + r"\..*?(?=^## |\Z)", txt, flags=re.M | re.S); return m.group(0) if m else ""
def field(txt, label):
    m = re.search(r"\*\*" + re.escape(label) + r"[^*]*\*\*[: ]*(.*)", txt); return m.group(1).strip() if m else ""
def code(txt): return "\n".join(re.findall(r"```[a-z]*\n(.*?)```", txt, flags=re.S))
header("TEL-D4-401")
txt = read(EVID)
if txt is None:
    print(f" [ERROR] Evidence file not found: {EVID}  (run the start command first)"); print(" Total Score: 0/5 (0%)"); sys.exit(1)
q = code(txt).lower()
live = None; why = ""
try:
    r = prom('topk(1, histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1d])) by (le, handler)))')
    live = (r[0]["metric"]["handler"], float(r[0]["value"][1])) if r else None
    why = "" if live else "Prometheus has no latency data yet (wait 5-10 minutes after start)"
except Exception as e: why = "Prometheus not reachable on localhost:9090 (run the start command): %s" % e
rule(1, bool(live and live[0] == "CheckoutController#processPayment" and 3.5 <= live[1] <= 5.0),
     "Live check: Prometheus p95 ranking puts CheckoutController#processPayment first at ~4.2 s" + (f" (now {live[0]} {live[1]:.2f}s)" if live else ""), why or "unexpected ranking - is the simulator the one from this kit?")
rule(2, "percentile(duration, 95)" in " ".join(q.split()) and "facet name" in q and "shopnow-production" in q,
     "NRQL ranking query: percentile(duration, 95) ... FACET name for ShopNow-Production",
     "Section 2 needs the NRQL query with percentile(duration, 95), FACET name and the app name")
rule(3, "timeseries" in q and "from transactionerror" in q and "facet error.class" in q,
     "NRQL trend (TIMESERIES) and error-impact query (FROM TransactionError ... FACET error.class)",
     "Add a TIMESERIES query and a TransactionError query faceted by error.class")
sl = field(txt, "Slowest transaction")
nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", sl)]
rule(4, "histogram_quantile" in q and "by (le, handler)" in " ".join(q.split()) and "processpayment" in sl.lower() and any(3.5 <= x <= 5.0 for x in nums),
     "PromQL cross-check (histogram_quantile ... by (le, handler)); slowest transaction named with its p95 (3.5-5 s)",
     "Add the PromQL query, and fill 'Slowest transaction and p95' with the name and the value in seconds")
rca = section(txt, 3); act = field(txt, "Recommended Action")
rule(5, "<<" not in txt and re.search(r"average|mean", rca.lower()) is not None and re.search(r"percentile|p95|tail|bimodal|slow", rca.lower()) is not None and len(rca.strip()) >= 80 and len(act) >= 20,
     "Evidence complete: no placeholders, RCA explains average vs percentile (>= 80 chars), recommendation given",
     "Fill every <<FILL_...>> field; the RCA must explain why the default overview / average hides the slow tail")
done()
