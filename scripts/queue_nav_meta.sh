#!/bin/zsh
# Wait for the navigation DR local planner, then meta-train the gradient-based learners from it.
cd "$(dirname "$0")/.."
log=runs/navigation/dr/seed0/log.jsonl
until [[ -f $log && $(wc -l < $log) -ge 250 && -f runs/navigation/dr/seed0/checkpoint.pt ]]; do sleep 60; done
sleep 30  # let the final checkpoint write finish
.venv/bin/python -m drone_autonomy.cli sweep --problems navigation --methods maml fomaml anil metasgd reptile --seeds 0 --workers 5
