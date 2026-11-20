#!/usr/bin/env python3
"""Day 1 lab controller: start / check / reset a scenario (s1, s2, s3).

Called by each scenario's validation_script.sh / validation_script.ps1.
Standard library only. Needs Docker + Docker Compose v2 for start/reset.
"""
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DAY1 = os.path.dirname(HERE)
PROJECT_PREFIX = "telemetry-d1"

SCENARIOS = {
    "s1": {
        "ticket": "TEL-D1-101",
        "title": "Checkout Is Slow but the Dashboard Looks Green",
        "evidence": "evidence_D1_1.json",
        "failure": ("Grafana RED dashboard shows green status and average latency of ~185ms, while "
                    "customers report 4.5s+ checkout timeouts. The panel query uses "
                    "'avg(payment_duration_seconds)' which flattens the bimodal distribution."),
        "ready": [("http://localhost:8081/health", "checkout-service"),
                  ("http://localhost:9090/-/ready", "Prometheus"),
                  ("http://localhost:3000/api/health", "Grafana")],
        "urls": [("Grafana RED dashboard", "http://localhost:3000   (admin / admin)"),
                 ("Prometheus", "http://localhost:9090"),
                 ("checkout-service", "http://localhost:8081  (metrics: /metrics)")],
        "wait_note": "Traffic is flowing. Give the dashboard 2-3 minutes of data before you judge it.",
        "baseline": [("dashboard_broken.json", "starter/grafana/dashboard_broken.json"),
                     ("prometheus.yml", "starter/conf/prometheus.yml"),
                     ("legacy_rules.yml", "starter/conf/legacy_rules.yml"),
                     ("evidence_D1_1.json", "starter/evidence/evidence_D1_1.json")],
        "rules": [
            ("p95 histogram_quantile query present", "histogram_quantile"),
            ("Correct bucket metric targeted", "payment_duration_seconds_bucket"),
            ("Rate aggregation applied inside bucket sum", "rate("),
            ("HTTP requests metric queried for errors", "http_requests_total"),
            ("Regex filter applied for 5xx errors", "status=~"),
        ],
    },
    "s2": {
        "ticket": "TEL-D1-102",
        "title": "Orders Fail for One Product: Follow the Trace",
        "evidence": "evidence_D1_2.md",
        "failure": ("Orders for promotional SKU 'PROD-7729' fail intermittently with generic 500 error "
                    "screens. Aggregate service metrics report healthy throughput, masking isolated "
                    "transaction failures."),
        "ready": [("http://localhost:8080/health", "frontend"),
                  ("http://localhost:8081/health", "checkout-service"),
                  ("http://localhost:8082/health", "payment-service"),
                  ("http://localhost:8083/health", "inventory-service"),
                  ("http://localhost:16686/", "Jaeger"),
                  ("http://localhost:3100/ready", "Loki"),
                  ("http://localhost:3000/api/health", "Grafana")],
        "urls": [("Jaeger UI", "http://localhost:16686"),
                 ("Grafana Explore (Loki)", "http://localhost:3000   (admin / admin)"),
                 ("Loki API", "http://localhost:3100"),
                 ("frontend", "http://localhost:8080  (POST /api/checkout {\"sku\": \"PROD-7729\"})")],
        "wait_note": "Orders are being placed. Wait ~1 minute, then look for failing checkout-service traces.",
        "baseline": [("evidence_D1_2.md", "starter/evidence/evidence_D1_2.md")],
        "rules": [
            ("Failing trace ID recorded and correlated", "trace id"),
            ("Failing span operation identified", "inventory.reserveStock"),
            ("Target promotional SKU identified", "PROD-7729"),
            ("Business exception captured from Loki", "StockReservationException"),
            ("Root cause and HTTP status mapping documented", "cycle-count audit"),
        ],
    },
    "s3": {
        "ticket": "TEL-D1-103",
        "title": "Six Alerts at Shift Start, One Real Problem",
        "evidence": "evidence_D1_3.json",
        "failure": ("Six simultaneous alerts fire in Alertmanager (CheckoutSlow, PaymentTimeout, "
                    "ProfileQueryDegraded, OrderHistory504, DiskIOWaitHigh, DatabaseQueueSaturation), "
                    "creating cognitive overload."),
        "ready": [("http://localhost:8083/health", "db/app telemetry simulator"),
                  ("http://localhost:9090/-/ready", "Prometheus"),
                  ("http://localhost:9093/-/ready", "Alertmanager"),
                  ("http://localhost:3000/api/health", "Grafana")],
        "urls": [("Alertmanager", "http://localhost:9093"),
                 ("Prometheus alerts", "http://localhost:9090/alerts"),
                 ("USE dashboard (Grafana)", "http://localhost:3000   (admin / admin)"),
                 ("PostgreSQL sessions (pg_stat_activity)", "http://localhost:8083/pg_stat_activity")],
        "wait_note": "Alerts need about 1 minute to go from Pending to Firing.",
        "baseline": [("use-alerts.yml", "starter/alerts/use-alerts.yml"),
                     ("prometheus.yml", "starter/conf/prometheus.yml"),
                     ("evidence_D1_3.json", "starter/evidence/evidence_D1_3.json")],
        "rules": [
            ("Primary causal alert identified", "DatabaseQueueSaturation"),
            ("Corroborating infrastructure alert recorded", "DiskIOWaitHigh"),
            ("Rogue query PID identified", "9182"),
            ("Target database resource identified", "PostgreSQL"),
            ("Remediation read replica routing proposed", "replica"),
        ],
    },
}


# ----------------------------------------------------------------- helpers
def sc_dir(s):
    return os.path.join(DAY1, s)


def banner(text):
    print("=" * 51)
    print(" " + text)
    print("=" * 51)


def project_name(s):
    return PROJECT_PREFIX + "-" + s


def compose_base(s):
    return ["docker", "compose", "-p", project_name(s), "-f", os.path.join(sc_dir(s), "lab", "docker-compose.yml")]


def docker_ready():
    try:
        r = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if r.returncode != 0:
            raise OSError
    except OSError:
        print(" [ERROR] Docker Compose v2 was not found. Install Docker (24+) and re-run.")
        return False
    r = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if r.returncode != 0:
        print(" [ERROR] The Docker daemon is not running (or you lack permission). Start Docker and re-run.")
        return False
    return True


def http_get(url, auth=None, timeout=4):
    req = urllib.request.Request(url)
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def restore_baseline(s):
    """Put starter files back to their original state; keep a .bak of anything changed."""
    cfg = SCENARIOS[s]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for base_name, rel in cfg["baseline"]:
        src = os.path.join(sc_dir(s), "lab", "baseline", base_name)
        dst = os.path.join(sc_dir(s), rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            with open(src, "rb") as a, open(dst, "rb") as b:
                if a.read() == b.read():
                    continue
            shutil.copyfile(dst, dst + ".bak-" + stamp)
            print("   saved your changed %s as %s.bak-%s" % (rel, os.path.basename(dst), stamp))
        shutil.copyfile(src, dst)       # copyfile keeps the inode, so Docker bind mounts stay valid


# ----------------------------------------------------------------- actions
def stop_stack(s):
    # Stop the current unique project and the legacy shared project name used
    # by earlier package revisions. This prevents stale containers from holding
    # ports when a participant upgrades an already-extracted lab directory.
    compose_file = os.path.join(sc_dir(s), "lab", "docker-compose.yml")
    for project in (project_name(s), "telemetry-d1"):
        cmd = ["docker", "compose", "-p", project, "-f", compose_file,
               "down", "-v", "--remove-orphans"]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if r.returncode != 0:
            # A not-yet-created project is normal; surface other errors for diagnosis.
            msg = (r.stderr or r.stdout or "").strip()
            if msg and "no such" not in msg.lower() and "not found" not in msg.lower():
                print(" [WARN] Could not fully stop %s: %s" % (project, msg[-500:]))


def stop_all_stacks():
    for scenario in ("s1", "s2", "s3"):
        stop_stack(scenario)


def do_reset(s):
    cfg = SCENARIOS[s]
    banner("Resetting Scenario %s..." % cfg["ticket"])
    if not docker_ready():
        print(" [ERROR] Docker is required to reset the running scenario safely.")
        return 1
    print(" Stopping the scenario stack and removing its named volumes...")
    stop_stack(s)
    restore_baseline(s)
    print("Baseline state restored. Evidence backups, if any, remain beside the starter file.")
    return 0


def do_start(s):
    cfg = SCENARIOS[s]
    if not docker_ready():
        return 1
    print(" Stopping any previously active Day 1 scenario to prevent port conflicts...")
    stop_all_stacks()
    # Restore the selected scenario's pristine starter files before deployment.
    if do_reset(s) != 0:
        return 1
    banner("Initializing Incident: %s" % cfg["ticket"])
    print(" " + cfg["title"])
    print("=" * 51)
    print(" Building and starting the ShopNow lab stack (first run downloads images, this can take")
    print(" several minutes)...")
    # Validate the Compose model before creating containers.
    config_check = subprocess.run(compose_base(s) + ["config", "-q"])
    if config_check.returncode != 0:
        print(" [ERROR] Compose configuration validation failed. No containers were started.")
        return 1
    r = subprocess.run(compose_base(s) + ["up", "-d", "--build"])
    if r.returncode != 0:
        print(" [ERROR] docker compose failed. Check the scenario-specific ports and build logs.")
        print("         Run: docker compose -p %s -f lab/docker-compose.yml logs --tail=100" % project_name(s))
        return 1

    print(" Waiting for services to become ready...")
    pending = list(cfg["ready"])
    deadline = time.time() + 240
    while pending and time.time() < deadline:
        for item in list(pending):
            try:
                st, _ = http_get(item[0])
                if st < 400:
                    print("   [UP] %s" % item[1])
                    pending.remove(item)
            except Exception:
                pass
        if pending:
            time.sleep(3)
    if pending:
        print(" [ERROR] Services did not become ready: " + ", ".join(p[1] for p in pending))
        print("         Run: docker compose -p %s -f lab/docker-compose.yml ps" % project_name(s))
        print("         Run: docker compose -p %s -f lab/docker-compose.yml logs --tail=100" % project_name(s))
        return 1

    print(" [PASS] All configured readiness endpoints returned HTTP success.")
    print("")
    print("Observed Failure: " + cfg["failure"])
    print("")
    print("Open these:")
    for name, url in cfg["urls"]:
        print("  %-38s %s" % (name, url))
    print("")
    print(cfg["wait_note"])
    print("Your Mission: Follow guidelines in starter/README_START_HERE.txt")
    print("Fill evidence template in: starter/evidence/" + cfg["evidence"])
    print("Then validate with: ./validation_script.sh check")
    return 0


def grafana_exprs(uid):
    user = os.getenv("GRAFANA_USER", "admin")
    pwd = os.getenv("GRAFANA_PASSWORD", "admin")
    _, body = http_get("http://localhost:3000/api/dashboards/uid/" + uid, auth=user + ":" + pwd)
    exprs = []

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("expr"), str):
                exprs.append(o["expr"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.loads(body))
    return exprs


def do_check(s):
    cfg = SCENARIOS[s]
    evidence = os.path.join(sc_dir(s), "starter", "evidence", cfg["evidence"])
    banner("Validating Solution for %s" % cfg["ticket"])
    if not os.path.isfile(evidence):
        print(" [ERROR] Evidence file not found: " + evidence)
        print(" Total Score: 0/5 (0%)")
        return 1
    text = open(evidence, encoding="utf-8", errors="replace").read()
    if s in ("s1", "s3"):
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            print(" [FAIL] Evidence must be valid JSON: %s" % exc)
            return 1
    placeholders = ("<<FILL_", "<<PASTE_", "<<EXPLAIN_")
    if any(token in text for token in placeholders):
        print(" [FAIL] Evidence still contains unfilled template placeholders.")
        print("        Complete every field before running check again.")
        return 1

    results = []
    low = text.lower()
    rules = cfg["rules"]
    if s == "s2":
        # Trace IDs are generated at runtime. Validate a real 32-hex ID and
        # ensure the Jaeger URL and Loki query use that same captured ID.
        trace_match = re.search(r"(?im)^\s*(?:-\s*)?(?:\*\*)?(?:trace id|captured trace id)(?::)?(?:\*\*)?\s*:?[ \t]*`?([0-9a-f]{32})`?", text)
        trace_id = trace_match.group(1) if trace_match else None
        jaeger_ok = bool(trace_id and re.search(r"http://localhost:16686/trace/" + re.escape(trace_id) + r"\b", text, re.I))
        logql_ok = bool(trace_id and re.search(r'\{app="inventory-service"\}\s*\|=\s*"' + re.escape(trace_id) + r'"', text, re.I))
        results.append(bool(trace_id and jaeger_ok and logql_ok))
        print("  [%s] Rule 1: Runtime Trace ID recorded and reused in Jaeger URL + Loki query" % ("PASS" if results[-1] else "FAIL"))
        rules = rules[1:]
    for i, (label, needle) in enumerate(rules, len(results) + 1):
        ok = needle.lower() in low
        if s == "s2" and "status mapping" in label.lower():
            audit_phrase = ("cycle-count audit" in low) or ("cycle count audit" in low)
            ok = audit_phrase and "409" in low and "500" in low
        results.append(ok)
        if ok:
            print("  [PASS] Rule %d: %s" % (i, label))
        else:
            print("  [FAIL] Rule %d: %s (missing pattern: %s)" % (i, label, needle))

    if s == "s1":     # live checks against the participant's Grafana dashboard
        for url, name in cfg["ready"]:
            try:
                good = http_get(url)[0] < 400
            except Exception:
                good = False
            if not good:
                print("  [FAIL] Environment endpoint unavailable: %s (%s)" % (name, url))
                print("  [INFO] Restart the scenario with './validation_script.sh start'.")
                return 1
        n = len(cfg["rules"])
        try:
            exprs = grafana_exprs("red-checkout")
            err = None
        except Exception as exc:
            exprs, err = [], str(exc)
        live = [
            ("Live: Grafana dashboard uses p95 histogram_quantile on payment_duration_seconds_bucket",
             any("histogram_quantile" in e and "payment_duration_seconds_bucket" in e and "rate(" in e for e in exprs)),
            ("Live: Grafana dashboard has a 5xx Errors panel (http_requests_total, status=~\"5..\")",
             any("http_requests_total" in e and re.search(r'status\s*=~\s*"5', e) for e in exprs)),
        ]
        for j, (label, ok) in enumerate(live, n + 1):
            results.append(ok)
            print("  [%s] Rule %d: %s" % ("PASS" if ok else "FAIL", j, label))
        if err:
            print("  [INFO] Could not read the dashboard from Grafana (%s)." % err)
            print("         Is the lab running ('start')? If you changed the Grafana admin password,")
            print("         set GRAFANA_USER / GRAFANA_PASSWORD before running check.")
        elif not all(r for r in results[n:]):
            print("  [INFO] Save your dashboard in Grafana (Save dashboard) so the live checks can see it.")
    else:             # S2/S3 evidence checks require their live lab to be running.
        up = []
        for url, name in cfg["ready"]:
            try:
                good = http_get(url)[0] < 400
            except Exception:
                good = False
            up.append(good)
            if not good:
                print("  [FAIL] Environment endpoint unavailable: %s (%s)" % (name, url))
        if not all(up):
            print("  [INFO] Restart the scenario with './validation_script.sh start' and wait for readiness.")
            return 1

    passed, total = sum(results), len(results)
    score = passed * 100 // total
    print("-" * 51)
    print(" Test Summary: %d / %d checks passed (%d%%)" % (passed, total, score))
    print("-" * 51)
    if passed == total:
        print(" [SUCCESS] All validation checks passed successfully!")
        return 0
    print(" [INCOMPLETE] Please address failed checks and re-run.")
    return 1


def main(argv):
    if len(argv) < 3 or argv[1] not in SCENARIOS or argv[2] not in ("start", "check", "reset"):
        print("Usage: labctl.py {s1|s2|s3} {start|check|reset}")
        return 2
    return {"start": do_start, "check": do_check, "reset": do_reset}[argv[2]](argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
