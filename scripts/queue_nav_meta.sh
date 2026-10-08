#!/bin/zsh
# Wait for the navigation DR local planner of a seed, then meta-train the gradient-based learners from it.
# Usage: scripts/queue_nav_meta.sh [seed]
cd "$(dirname "$0")/.."
seed=${1:-0}
log=runs/navigation/dr/seed$seed/log.jsonl
until [[ -f $log && $(wc -l < $log) -ge 250 && -f runs/navigation/dr/seed$seed/checkpoint.pt ]]; do sleep 60; done
sleep 30  # let the final checkpoint write finish
.venv/bin/python -m drone_autonomy.cli sweep --problems navigation --methods maml fomaml anil metasgd reptile --seeds $seed --workers 5
