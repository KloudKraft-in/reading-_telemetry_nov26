#!/usr/bin/env python3

import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D5_2.md")
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

header("TEL-D5-502")
txt = load(); low = txt.lower(); sec = sections(txt)
s1, s2, s3, s4 = (sec.get(k, "") for k in ("1", "2", "3", "4"))
uuid = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", low)
rule(1, "task timed out" in low and "filter" in code(s2).lower() and uuid is not None,
     "Logs Insights: timed-out invocation found (query + Lambda request id)",
     "Section 2 needs your Logs Insights query; Section 1 the request id of one timed-out invocation")
trace = re.search(r"1-[0-9a-f]{8}-[0-9a-f]{24}", low)
rule(2, trace is not None and "s3:putobject" in low, "X-Ray: trace id recorded and subsegment S3:PutObject identified",
     "Record the trace id (1-xxxxxxxx-...) and name the stalled subsegment S3:PutObject")
dur = re.search(r"\b29\.\d+\s*(s|sec)|\b29[0-9]{3}\s*ms", low)
rule(3, dur is not None and "shopnow-invoices-archive" in low, "Stalled call quantified: S3:PutObject ~29.x s on the shopnow-invoices-archive bucket",
     "Give the subsegment duration (about 29.7 s) and the bucket name")
rule(4, "vpc" in s3.lower() and "endpoint" in s3.lower() and re.search(r"route|private subnet|no internet|nat", s3.lower()) is not None,
     "Root cause: Lambda in a private VPC subnet without an S3 gateway endpoint / route",
     "Section 3 must explain the missing S3 gateway endpoint (VPC, private subnet, route)")
fix = s4.lower()
rule(5, "<<" not in txt and "invoice stored" in fix and len(field(s4, "Recommended Action")) >= 20,
     "Fix verified (log line 'invoice stored' after the endpoint exists), no placeholders, recommendation given",
     "Section 4 needs the after-fix log message 'invoice stored' and a recommended action; fill every <<FILL_...>> field")
done()
