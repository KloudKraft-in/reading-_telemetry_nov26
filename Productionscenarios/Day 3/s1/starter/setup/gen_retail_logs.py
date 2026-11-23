#!/usr/bin/env python3
"""TEL-D3-301 data generator (seeded, standard library only).
Writes web/checkout logs for the LAST 4 HOURS (UTC) so 'earliest=-4h' works in Splunk.
Story: a release ~2 h ago breaks host web-prod-04 (corrupted assembly): 8.4 % checkout errors, 92 % of them on web-prod-04.
Usage: python3 gen_retail_logs.py <output_dir>
"""
import os, random, sys
from datetime import datetime, timedelta, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "data"
os.makedirs(OUT, exist_ok=True)
rnd = random.Random(30101)
now = datetime.now(timezone.utc).replace(microsecond=0)
start, release = now - timedelta(hours=4), now - timedelta(hours=2)
HOSTS = ["web-prod-01", "web-prod-02", "web-prod-03", "web-prod-04"]
F = "%Y-%m-%d %H:%M:%S"

# ---- retail_checkout: 3000 events, exactly 252 errors (8.4 %), 232 of them on web-prod-04 (92.06 %), all after the release
N_TOTAL, N_ERR, N_ERR_04 = 3000, 252, 232
CODES_04 = ["ERR-4011"] * 150 + ["ERR-4012"] * 60 + ["ERR-5003"] * 22
CODES_OT = ["ERR-5003"] * 12 + ["ERR-4012"] * 8
rnd.shuffle(CODES_04); rnd.shuffle(CODES_OT)
events = []  # (time, host, text)
sid = 90000
def ts_between(a, b): return a + timedelta(seconds=rnd.uniform(0, (b - a).total_seconds()))

# error sessions on web-prod-04 (retries stretch the session over 11-40 s)
for code in CODES_04:
    sid += 1; t0 = ts_between(release, now - timedelta(minutes=2)); s = f"sess-{sid}"
    events.append((t0, "web-prod-04", f'status_code=OK session_id={s} resp_secs=0.4 msg="cart validated"'))
    events.append((t0 + timedelta(seconds=rnd.randint(11, 40)), "web-prod-04",
                   f'status_code={code} session_id={s} resp_secs={rnd.uniform(9, 15):.1f} msg="Corrupted local assembly"'))
# the other 20 errors on the other hosts
for code in CODES_OT:
    sid += 1; t0 = ts_between(release, now - timedelta(minutes=2)); h = rnd.choice(HOSTS[:3]); s = f"sess-{sid}"
    events.append((t0, h, f'status_code={code} session_id={s} resp_secs={rnd.uniform(2, 4):.1f} msg="upstream timeout"'))
# healthy sessions fill the remaining events (1-3 events each, 1-6 s long)
while len(events) < N_TOTAL:
    sid += 1; t0 = ts_between(start, now - timedelta(minutes=1)); h = rnd.choice(HOSTS); s = f"sess-{sid}"
    for i in range(rnd.randint(1, 3)):
        if len(events) >= N_TOTAL: break
        events.append((t0 + timedelta(seconds=i * rnd.randint(1, 3)), h,
                       f'status_code=OK session_id={s} resp_secs={rnd.uniform(0.1, 0.9):.1f} msg="{rnd.choice(["cart validated","payment authorised","order placed"])}"'))

# ---- retail_web: ~2400 access lines, mostly 200; a few 5xx on web-prod-04 after the release
web = []
for i in range(2400):
    t = ts_between(start, now - timedelta(minutes=1)); h = rnd.choice(HOSTS)
    st = 200 if rnd.random() < 0.985 else rnd.choice([404, 301])
    if h == "web-prod-04" and t >= release and rnd.random() < 0.05: st = 500
    web.append((t, h, f'method=GET path={rnd.choice(["/","/cart","/checkout","/product/42","/search"])} status={st} bytes={rnd.randint(300,9000)}'))

def dump(rows, prefix):
    for h in HOSTS:
        with open(os.path.join(OUT, f"{prefix}-{h}.log"), "w") as f:
            for t, host, text in sorted(r for r in rows if r[1] == h):
                f.write(f"{t.strftime(F)} host={host} {text}\n")
dump(events, "checkout"); dump(web, "web")

err = [e for e in events if "status_code=ERR-" in e[2]]
e04 = [e for e in err if e[1] == "web-prod-04"]
print(f"checkout events {len(events)} | errors {len(err)} ({100*len(err)/len(events):.1f} %) | web-prod-04 share {100*len(e04)/len(err):.1f} % | web events {len(web)}")
