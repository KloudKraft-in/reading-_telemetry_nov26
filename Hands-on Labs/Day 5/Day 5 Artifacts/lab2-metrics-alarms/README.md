# Day 5 Lab 2 (AWS) — artifacts

| File | Use |
|---|---|
| `shop-metrics-lab.yaml` | CloudFormation template (console: CloudFormation → Create stack → Upload a template file; parameter Seat, optional AlertEmail). Creates the generator Lambda shop-orders-<seat>, its EventBridge schedule (every minute), the SNS topic shop-alerts-<seat> and a 1-day log group. |
| `shop-orders-generator.py` | Readable copy of the generator (EMF lines; Lambda environment variable FAULT = none, payment-errors or payment-slow). |
| `dashboard-template.json` | CloudWatch dashboard source. Replace `__SEAT__` and `__REGION__` (find and replace in the editor), then paste in Dashboards → Create → Actions → View/edit source. |
| `metrics-insights-queries.txt` | Metrics Insights and metric-math expressions of Task 2. |

Cost: about 6 custom metrics, 3 alarms and 1 dashboard per learner — a few US cents per learner when cleaned up the same day (estimate; custom metrics and alarms are billed per month, check current pricing). Clean-up: delete the stack, then the alarms and the dashboard (created by hand).
