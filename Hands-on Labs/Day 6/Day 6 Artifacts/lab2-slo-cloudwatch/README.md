# Day 6 Lab 2 (AWS CloudWatch) — artifacts

| File | Use |
|---|---|
| `shop-slo-lab.yaml` | CloudFormation template (console: CloudFormation → Create stack → Upload a template file; parameter Seat). Creates a t3.micro EC2 instance, a 2 GiB gp3 EBS volume, two log groups and the instance role. Everything is created in your one allowed region. |
| `shop_sim.py`, `shopmodel.py` | Shop simulator started by the instance at boot (custom metrics via put-metric-data and log lines). Readable copies. |
| `slo-report.py` | Offline 28-day SLO report from `data/sli-history.csv` and `data/incidents.csv` (SLI, budget, consumed %, biggest incident, MTTD/MTTR). |
| `data/` | 28 days of synthetic SLI history and incidents. |
| `INSTRUCTOR-learner-iam-policy.json` | Instructor only: restricts each learner to one region and own-seat resources. Not for learners. |

Cost: one t3.micro, a 2 GiB gp3 volume, custom metrics, alarms and logs per learner — small if cleaned up the same day (estimate; check current pricing). Alarms have no notification actions. Clean-up: delete the stack, then the alarms created by hand.
