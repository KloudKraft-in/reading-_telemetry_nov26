# Day 5 Lab 1 (AWS) — artifacts

| File | Use |
|---|---|
| `shop-checkout-lab.yaml` | CloudFormation template (console: CloudFormation → Create stack → Upload a template file). Creates shop-checkout-<seat>, shop-order-driver-<seat>, their two IAM roles and a log group with 1-day retention. |
| `shop-checkout-app.py` | Readable copy of the function code that is embedded in the template (standard library only, writes X-Ray subsegments over UDP). |
| `shop-order-driver.py` | Readable copy of the driver (60 orders, 1 per second, ≈ 90 s). |
| `logs-insights-queries.txt` | Every query of Tasks 2 and 4. |
| `xray-filter-expressions.txt` | Every filter expression of Task 3. |

Cost: a few cents per learner. Clean-up: delete the CloudFormation stack (removes functions, roles and log group).
