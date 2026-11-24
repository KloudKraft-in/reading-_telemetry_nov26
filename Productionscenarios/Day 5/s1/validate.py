#!/usr/bin/env python3

import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "starter", "evidence", "evidence_D5_1.md")
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

header("TEL-D5-501")
txt = load(); low = txt.lower(); sec = sections(txt)
s1, s2, s3, s4 = (sec.get(k, "") for k in ("1", "2", "3", "4"))
q = code(s2).lower()
rule(1, all(k in q for k in ("dependencies", "summarize", "countif", "by target")),
     "Ranking query: dependencies | summarize ... countif ... by target",
     "Section 2 must contain your ranking query (dependencies, summarize, countif, by target)")
cul, rate = field(s1, "Culprit"), field(s1, "Failure rate")
rule(2, "api.external-fraud.io" in cul.lower() and "42.4" in rate and "212" in rate and "500" in rate,
     "Culprit isolated with its numbers (api.external-fraud.io, 212 of 500 = 42.4 %)",
     "Section 1: culprit must name the vendor; failure-rate line must give failed calls, total calls and the percentage")
rule(3, all(k in q for k in ("join kind=inner", "operation_id", "exceptions")) and "504" in low and "taskcanceledexception" in low,
     "Correlation: join kind=inner on operation_Id with exceptions; 504 and TaskCanceledException recorded",
     "Section 2 needs the join query; the evidence must name the HTTP code 504 and the exception type")
rule(4, "inventory-svc" in s3.lower() and "404" in s3 and re.search(r"expected|benign|harmless|normal|not an incident|not the incident", s3.lower()) is not None,
     "Judgment: inventory-svc 404 recognised as expected, not the incident",
     "Section 3 (RCA) must explain why inventory-svc / 404 is not the cause")
first = field(s1, "First failure")
act = field(s4, "Recommended Action")
ok5 = "<<" not in txt and re.search(r"\d{1,2}:\d{2}", first) and len(s3.strip()) >= 80 and re.search(r"timeout|retry|circuit|fallback|alert|vendor|escalat", act.lower())
rule(5, bool(ok5), "Evidence complete: no placeholders, first-failure time, RCA >= 80 chars, concrete recommended action",
     "Fill every <<FILL_...>> field, give the first failure time (HH:MM), explain the RCA and state a recommended action")
done()
