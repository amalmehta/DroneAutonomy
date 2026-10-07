#!/bin/zsh
# After every navigation seed-1 run has finished training, benchmark them under the corrected room protocol.
cd "$(dirname "$0")/.."
ready() {
  for m in dr e2e_dr pearl rl2 maml fomaml anil metasgd reptile; do
    case $m in dr|e2e_dr) n=250;; pearl) n=200;; rl2) n=120;; reptile) n=50;; *) n=60;; esac
    f=runs/navigation/$m/seed1/log.jsonl
    [[ -f $f && $(wc -l < $f) -ge $n ]] || return 1
  done
  return 0
}
until ready; do sleep 120; done
sleep 60
.venv/bin/python -m drone_autonomy.cli bench --problems navigation --seeds 1 --workers 5
