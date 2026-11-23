# New Relic simulator (instructor only, UNTESTED)

Why: TEL-D4-401 needs the NRQL Query builder, so data must reach a New Relic account. 40 learners cannot each run an agent.

1. Create one New Relic account (free tier). Add learners as Basic users (so they can run NRQL).
2. `cp .env.example .env` and put the account's licence key in `.env`. Do not share it or commit it.
3. `docker compose up -d --build` on the instructor machine at least 30 minutes before class.
4. In New Relic confirm `SELECT count(*) FROM Transaction WHERE appName='ShopNow-Production' SINCE 5 minutes ago` is > 0 and that `FROM TransactionError` returns rows.
5. Stop after class: `docker compose down`.

Not verified: free-tier data limits for 40 concurrent users, Basic-user access to NRQL, `error.class` format.
Fallback if New Relic is not available: learners use the PromQL cross-check only, and the instructor shows the NRQL screens.
