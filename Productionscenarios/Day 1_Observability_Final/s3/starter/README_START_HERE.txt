TEL-D1-103 — Six Alerts at Shift Start, One Real Problem

RUN FROM: ~/day1/s3 (the scenario folder, not starter/)

1. Start/reset the scenario:
   ./validation_script.sh start
   Windows PowerShell: .\validation_script.ps1 start
2. Wait for simulator, Prometheus, Alertmanager and Grafana to report ready.
3. Allow about 60 seconds for the alert rules (for: 30s) to reach Firing.
4. Open Alertmanager: http://localhost:9093 → Alerts.
5. Open Prometheus: http://localhost:9090/alerts. Review the six alert rules.
6. Open Grafana: http://localhost:3000 → Dashboards → USE Dashboard - PostgreSQL Primary.
7. Compare disk queue (~38) and I/O await (~280 ms) with CPU and memory.
8. Verify in Prometheus Graph:
   db_disk_queue_length{instance_role="primary"}
   db_disk_io_await_milliseconds{instance_role="primary"}
9. Open http://localhost:8083/pg_stat_activity and identify PID 9182 (analytics_batch / nightly-report-runner).
10. Explain the unindexed 90-day reporting query and its impact on PostgreSQL primary disk I/O.
11. Complete starter/evidence/evidence_D1_3.json with the causal alert, PID, PostgreSQL and read-replica mitigation.
12. Validate: ./validation_script.sh check
13. Reset after completion: ./validation_script.sh reset

This is a telemetry simulator, not a live PostgreSQL database. Do not execute a kill/terminate command against a real database process.
