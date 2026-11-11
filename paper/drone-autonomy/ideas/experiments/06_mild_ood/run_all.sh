#!/bin/zsh
# Runs every tracking method x seeds 0,1 on the mild-OOD split, 4 at a time.
cd "$(dirname "$0")"
PY=../../../../../.venv/bin/python
jobs_list=()
for p in tracking_residual; do for m in classical l1 dr dr_finetune maml fomaml anil metasgd reptile pearl rl2; do for s in 0 1; do jobs_list+=("$p $m $s"); done; done; done
for m in dr dr_finetune maml fomaml metasgd reptile; do for s in 0 1; do jobs_list+=("tracking_gains $m $s"); done; done
printf '%s\n' "${jobs_list[@]}" | xargs -P 4 -L 1 sh -c "$PY run.py \$0 \$1 \$2 >> results/log.txt 2>&1"
echo done >> results/log.txt
