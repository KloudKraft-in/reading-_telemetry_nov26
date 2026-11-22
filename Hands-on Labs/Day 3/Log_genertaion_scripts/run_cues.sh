#!/usr/bin/env bash
# run_cues.sh — runs the fault cue timeline of one Day 3 lab and prints each announcement.
# Usage: ./run_cues.sh lab3|lab4|lab5   (start it the moment the lab starts)
# SECS_PER_MIN=60 by default; use a tiny value (e.g. 0.02) for a dry run. DRY=1 prints without calling easyTravel.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; S="${SECS_PER_MIN:-60}"; START=$(date +%s)
run() { if [ -n "$DRY" ]; then echo "(dry) $*"; else "$@"; fi; }
at() { # at <minute> <label> <command...>
  local m="$1" label="$2"; shift 2
  local target; target=$(awk -v m="$m" -v s="$S" 'BEGIN{printf "%d", m*s}')
  local now=$(( $(date +%s) - START )); [ "$target" -gt "$now" ] && sleep $(( target - now ))
  echo "--- T+$m min · $label"; run "$@"
}
case "${1:?lab3|lab4|lab5}" in
  lab3) at 0  "deployment event"            "$DIR/post_deploy_event.sh"
        at 1  "fault ON"                    "$DIR/faultctl.sh" on
        at 34 "fault OFF (learners re-run Q10 after 2 min)" "$DIR/faultctl.sh" off;;
  lab4) at 0  "C0 baseline (fault off)"     "$DIR/faultctl.sh" off
        at 3  "C1 fault ON (Tasks 1-3)"     "$DIR/faultctl.sh" on
        at 16 "C2 fault OFF (learners create their log-based metric)" "$DIR/faultctl.sh" off
        at 23 "C3 fault ON (after metrics exist)" "$DIR/faultctl.sh" on
        at 28 "C4 fault OFF"                "$DIR/faultctl.sh" off;;
  lab5) at 0  "baseline (Tasks 1-2: learners create monitors)" "$DIR/faultctl.sh" off
        at 14 "C-A fault ON (Task 3)"       "$DIR/faultctl.sh" on
        at 21 "C-B fault OFF (recovery)"    "$DIR/faultctl.sh" off;;
  *) echo "usage: run_cues.sh lab3|lab4|lab5"; exit 1;;
esac
echo "Timeline finished."
