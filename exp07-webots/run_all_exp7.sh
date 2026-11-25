#!/bin/zsh
# All Experiment 7 runs (Part A, Part B, exercises 1 and 5). Each label gets _rN for repeat N.
cd /Users/mihika/webots-work
export WEBOTS_HOME=~/Applications/Webots.app
R=analysis/runs
run() { local world=$1 secs=$2 label=$3; shift 3
  if [[ -f $R/$label.csv ]]; then echo "skip $label"; return; fi
  echo "=== $label"; python3 tools/run_experiment.py $world --seconds $secs --name $label "$@" 2>&1 | grep -v '^Running'
}
for r in 1 2 3 4 5; do run swarm 120 swarm_default_r$r; done
for r in 1 2 3 4 5; do run swarm 120 swarm_cruise-0.9_r$r --set cruise=0.9; done
for c in 0.2 0.4 0.6 0.8 1.0; do for r in 1 2 3; do run swarm 120 swarm_cruise-${c}_r$r --set cruise=$c; done; done
for r in 1 2 3; do run pioneer 180 pioneer_default_r$r; done
for r in 1 2 3; do run pioneer 180 pioneer_bubble-0.15_r$r --set bubble=0.15; done
for r in 1 2 3; do run pioneer 180 pioneer_bubble-0.9_r$r --set bubble=0.9; done
for n in 0.001 0.003; do for r in 1 2 3; do run pioneer 180 pioneer_noise-${n}_r$r --lidar-noise $n; done; done
echo ALL DONE
