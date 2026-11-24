#!/usr/bin/env python3
"""Day 5 Lab 4 — runbook server: serves runbooks from ./runbooks at /runbooks/<file> on :9095 (the same program as the Lab 5 webhook sink);
serves runbooks from ./runbooks at /runbooks/<file>."""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        g = n.get("groupLabels", {})
        print(f"{self.path:<8} {n['status'].upper():<8} group={json.dumps(g, sort_keys=True)} alerts={len(n['alerts'])}", flush=True)
        for a in n["alerts"]:
            l, an = a["labels"], a.get("annotations", {})
            print(f"  - {l.get('alertname')} [{l.get('severity')}] {l.get('service', '-')} runbook={an.get('runbook_url', 'MISSING')}", flush=True)
        self.send_response(200); self.end_headers()
    def do_GET(self):
        f = os.path.join("runbooks", os.path.basename(self.path))
        if self.path.startswith("/runbooks/") and os.path.isfile(f):
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(open(f, "rb").read())
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *a): pass
print("webhook-sink listening on :9095", flush=True)
ThreadingHTTPServer(("0.0.0.0", 9095), H).serve_forever()
