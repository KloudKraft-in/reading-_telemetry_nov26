# Day 6 Lab 4 (AWS CloudWatch) — artifacts

| File | Use |
|---|---|
| `shop-bestpractices-lab.yaml` | CloudFormation template (parameter Seat): t3.micro EC2, 2 GiB gp3 EBS, log groups, CloudWatch agent config, instance role. One region only. |
| `shop_sim.py`, `shopmodel.py` | Simulator that writes shop metrics and logs; 3-hour backfill at boot. |
| `replay_alert.py`, `alert.conf` | Offline replay of multi-window burn-rate alert settings (long_period_min, short_period_min, burn_threshold) to compare noise vs detection time. |

Cost: one t3.micro, one small EBS volume, custom metrics, alarms and logs per learner — small if cleaned up the same day (estimate). Alarms have no notification actions. Clean-up: delete the stack, then alarms and the composite alarm created by hand.
