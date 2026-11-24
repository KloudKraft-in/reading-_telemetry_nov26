#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

if [ -f "$LAB_DIR/.env" ]; then
  set -a
  source "$LAB_DIR/.env"
  set +a
fi

if [ -z "${NEW_RELIC_LICENSE_KEY:-}" ]; then
  echo "ERROR: NEW_RELIC_LICENSE_KEY is not set."
  echo "Create $LAB_DIR/.env with:"
  echo "  NEW_RELIC_LICENSE_KEY=<your_ingest_license_key>"
  echo "  NEW_RELIC_ACCOUNT_ID=8684150"
  echo "  NEW_RELIC_REGION=US"
  exit 1
fi

NEW_RELIC_ACCOUNT_ID="${NEW_RELIC_ACCOUNT_ID:-8684150}"
NEW_RELIC_REGION="${NEW_RELIC_REGION:-US}"

chmod +x "$LAB_DIR/nr_easytravel_shipper.py" "$LAB_DIR/faultctl.sh"
"$LAB_DIR/faultctl.sh" off

pkill -f "nr_easytravel_shipper.py" 2>/dev/null || true
nohup python3 "$LAB_DIR/nr_easytravel_shipper.py" \
  --license-key "$NEW_RELIC_LICENSE_KEY" \
  --account-id "$NEW_RELIC_ACCOUNT_ID" \
  --region "$NEW_RELIC_REGION" \
  --flag "$HOME/obs-lab/control/fault.flag" >/tmp/nr_easytravel_shipper.log 2>&1 &

sleep 4
echo "=== New Relic easyTravel Telemetry Shipper Status ==="
tail -n 5 /tmp/nr_easytravel_shipper.log || true
echo ""
echo "Verify in New Relic (https://one.newrelic.com -> Query your data):"
echo "  SELECT count(*) FROM Transaction WHERE appName LIKE 'easyTravel%' SINCE 10 minutes ago"
echo "  SELECT uniques(appName) FROM Transaction SINCE 10 minutes ago"
