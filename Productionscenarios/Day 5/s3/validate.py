#!/usr/bin/env python3

import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D5_3.md")
PASS, TOTAL = [], 5
def read(p):
    try: return open(p, encoding="utf-8").read()
    except OSError: return None
def sections(txt):
    parts = re.split(r"^## ", txt, flags=re.M)
    return {p.split("\n", 1)[0].split(".")[0].strip(): p for p in parts[1:]}
def field(txt, label):
    m = re.search(r"\*\*" + re.escape(label) + r"[^*]*\*\*[: ]*(.*)", txt)
    return m.group(1).strip() if m else ""
def code(txt):
    return "\n".join(re.findall(r"```[a-z]*\n(.*?)```", txt, flags=re.S))
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
def load():
    txt = read(EVID)
    if txt is None:
        print(f" [ERROR] Evidence file not found: {EVID}  (run the start command first)"); print(" Total Score: 0/5 (0%)"); sys.exit(1)
    return txt

header("TEL-D5-503")
txt = load(); low = txt.lower(); sec = sections(txt)
EVDIR = os.path.join(HERE, "starter", "evidence")

# ---- the lab's metric pattern (repeats every hour, UTC); identical to starter/aws/pager-stack.yaml ----
def cpu_at(m): return 91.0 if 30 <= m <= 44 else 93.0 if m % 7 == 3 else 35.0 + (m * 7) % 10
def req_at(m): return 600 + (m * 13) % 80
def err_at(m): return round(req_at(m) * 0.06) if 50 <= m <= 57 else (3 if m % 5 == 2 else 0)

def simulate(kind, period_s, n, m, thr, hours=4):
    """CloudWatch M-of-N evaluation on the lab pattern. Returns (transitions to ALARM per hour, minute-of-hour at which each ALARM starts)."""
    p = period_s // 60
    mins = hours * 60
    windows = []
    for w in range(mins // p):
        ts = range(w * p, (w + 1) * p)
        if kind == "cpu":
            windows.append(sum(cpu_at(t % 60) for t in ts) / p)
        else:
            windows.append(100.0 * sum(err_at(t % 60) for t in ts) / sum(req_at(t % 60) for t in ts))
    state, entries = False, []
    for j in range(len(windows)):
        if j + 1 < n: continue
        breaching = sum(1 for v in windows[j + 1 - n:j + 1] if v > thr)
        now = breaching >= m
        end_min = (j + 1) * p
        if now and not state and end_min > mins // 2: entries.append(end_min % 60)
        state = now
    return len(entries) / 2.0, entries            # the counting window is the last 2 hours

def num(s):
    mm = re.search(r"-?\d+(?:\.\d+)?", s or "")
    return float(mm.group(0)) if mm else None

def f(label): return field(txt, label)

# --- Rule 1: diagnosis - the noisy episodes were counted on the graph, the noisy settings named ---
untuned_cpu, _ = simulate("cpu", 60, 1, 1, 80)
untuned_err, _ = simulate("err", 60, 1, 1, 0)
c1, c2 = num(f("CPU alarm: breaching episodes")), num(f("Error alarm: breaching episodes"))
s2 = sections(txt).get("2", "").lower(); s3 = sections(txt).get("3", "").lower()
counts_ok = c1 is not None and c2 is not None and abs(c1 - untuned_cpu) <= 2 and abs(c2 - untuned_err) <= 2
why_ok = bool(re.search(r"one datapoint|1 datapoint|single datapoint|one minute|1 minute|one-minute|one sample|single", s2 + s3)
              and re.search(r"ratio|percent|%|requests|any error|threshold (of )?0|> ?0", s2 + s3))
rule(1, counts_ok and why_ok,
     "Diagnosis: episodes counted on the alarm graphs (about %d for CPU, %d for errors per hour) and both noisy settings explained" % (untuned_cpu, untuned_err),
     "count the separate breaches in the last 60 min on each alarm graph (CPU about %d, errors about %d, +/-2) and explain: 1 datapoint is enough, and the error alarm counts failures instead of a ratio" % (untuned_cpu, untuned_err))

def alarm(prefix):
    g = lambda k: f(prefix + " - " + k)
    return {"stat": g("Statistic").strip().lower(), "thr": num(g("Threshold")), "period": num(g("Period")), "n": num(g("Evaluation periods")),
            "m": num(g("Datapoints to alarm")), "missing": g("Treat missing data").lower(), "sev": g("Severity").strip().lower(),
            "url": g("Runbook URL").strip(), "metrics": g("Metrics used").lower()}
cpu, err = alarm("CPU alarm"), alarm("Error alarm")
def complete(a, need_stat=True):
    return all(a[k] is not None for k in ("thr", "period", "n", "m")) and a["period"] % 60 == 0 and 60 <= a["period"] <= 600 and 1 <= a["m"] <= a["n"] <= 24

# --- Rule 2: CPU alarm behaves (sustained only) ---
cpu_ok, cpu_why = False, "fill the CPU alarm settings (statistic, threshold, period, evaluation periods, datapoints to alarm)"
if complete(cpu):
    tr, ent = simulate("cpu", int(cpu["period"]), int(cpu["n"]), int(cpu["m"]), cpu["thr"])
    hold = cpu["m"] * cpu["period"]
    cpu_ok = cpu["stat"].startswith("avg") or cpu["stat"].startswith("average")
    cpu_ok = cpu_ok and 60 <= cpu["thr"] <= 95 and 600 <= hold <= 840 and tr == 1.0 and all(30 <= e <= 50 for e in ent) and "not" in cpu["missing"] and "breach" in cpu["missing"]
    cpu_why = (f"statistic {cpu['stat']}, threshold {cpu['thr']:g}, {int(cpu['m'])} of {int(cpu['n'])} x {int(cpu['period'])} s = {int(hold)} s to alarm, "
               f"simulated {tr:g} ALARM per hour (need exactly 1 during the :30-:44 incident), missing data '{cpu['missing']}' (need: not breaching); "
               "need Average, threshold 60-95, 600-840 s of sustained breach")
rule(2, cpu_ok, "CPU alarm: Average > ~80 for 10 minutes, not breaching on missing data; ignores one-minute spikes, catches the sustained incident", cpu_why)

# --- Rule 3: error alarm is a ratio and behaves ---
err_ok, err_why = False, "fill the error alarm settings and name the two metrics (Errors, Requests)"
expr = (f("Error alarm - Metrics used") + " " + code(sections(txt).get("2", ""))).lower()
if complete(err):
    tr, ent = simulate("err", int(err["period"]), int(err["n"]), int(err["m"]), err["thr"])
    hold = err["m"] * err["period"]
    ratio = ("errors" in expr and "requests" in expr and re.search(r"100\s*\*|\*\s*100", expr) is not None and "/" in expr)
    err_ok = ratio and 3 <= err["thr"] <= 8 and 180 <= hold <= 300 and tr == 1.0 and all(e >= 50 or e == 0 for e in ent) and "not" in err["missing"] and "breach" in err["missing"]
    err_why = (f"ratio expression with Errors, Requests and 100*: {'yes' if ratio else 'NO'}; threshold {err['thr']:g}; {int(err['m'])} of {int(err['n'])} x {int(err['period'])} s = {int(hold)} s to alarm; "
               f"simulated {tr:g} ALARM per hour (need exactly 1 during the :50-:57 incident); missing data '{err['missing']}'; need 100*m2/m1 > 3-8 for 180-300 s")
rule(3, err_ok, "Error alarm: metric-math ratio 100*Errors/Requests > ~5 % for 3 minutes; ignores the 0.5 % background, catches the 6 % incident", err_why)

# --- Rule 4: severity and runbook ---
def url_ok(a, rb): return re.match(r"https?://\S+", a["url"]) is not None and rb.lower() in a["url"].lower()
rule(4, cpu["sev"] == "warning" and err["sev"] == "critical" and url_ok(cpu, "RB-CPU-001") and url_ok(err, "RB-CHK-002"),
     "Severity: CPU = warning, errors = critical; each alarm has its runbook URL (RB-CPU-001, RB-CHK-002)",
     f"found CPU severity={cpu['sev'] or 'missing'}, errors={err['sev'] or 'missing'}; runbook URLs: {cpu['url'] or 'missing'} / {err['url'] or 'missing'}")

# --- Rule 5: dashboards exported and evidence complete ---
def dash(name):
    t = read(os.path.join(EVDIR, name))
    if t is None: return None
    try: return json.loads(t)
    except ValueError: return {}
def widgets(d): return [w for w in d.get("widgets", []) if isinstance(w, dict) and w.get("type") != "text"]
def links_to(d, name): return any(w.get("type") == "text" and name.lower() in json.dumps(w.get("properties", {})).lower() for w in d.get("widgets", []))
t1, t2 = dash("tier1.json"), dash("tier2.json")
ok5 = bool("<<" not in txt and t1 and t2 and 3 <= len(widgets(t1)) <= 6 and len(widgets(t2)) >= 8 and links_to(t1, "Tier2") and links_to(t2, "Tier1"))
rule(5, ok5, "Dashboards exported (tier1.json: 3-6 widgets + a text widget linking to Tier2; tier2.json: >= 8 widgets + a text widget linking to Tier1) and evidence complete",
     "save both dashboard sources (Actions -> View/edit source) as starter/evidence/tier1.json and tier2.json, add the markdown link widgets, and fill every <<FILL_...>> field")
done()
