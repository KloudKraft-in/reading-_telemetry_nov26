"""Deterministic model of the lab shop (used by shop_sim.py on the lab instance).
The incident repeats every 30 minutes: minutes :20-:24 and :50-:54 (UTC). The data volume fills up and checkout fails."""
def is_bad(m): return 20 <= (m % 30) < 25
def minute_stats(m):
    """returns (requests, errors_5xx, latency_p95_ms, data_disk_used_pct) for minute-of-hour m"""
    k = m % 30
    req = 90 + (k * 7) % 13
    if is_bad(m): return req, int(req * 0.8), 2100 + (k * 13) % 90, [90, 95, 98, 99, 100][k - 20]
    return req, (1 if k % 9 == 0 else 0), 380 + (k * 11) % 60, 60 + (k % 4)
def incident():
    rows = [minute_stats(m) for m in range(20, 25)]
    req = sum(r[0] for r in rows); err = sum(r[1] for r in rows)
    return dict(requests=req, errors=err, error_pct=100.0 * err / req, burn=100.0 * err / req / 0.5, disk_peak=max(r[3] for r in rows))
if __name__ == "__main__": print(incident())
