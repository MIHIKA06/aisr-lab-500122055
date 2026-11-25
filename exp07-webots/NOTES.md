# Experiment 7: Webots reactive swarm and lidar navigation — run notes

Project: github.com/reshamrajs/webots-robotics-sim, cloned outside this repo. Only my changed file,
run script, analysis code, run CSVs and figures are committed here.

Environment: macOS 27, Apple M5. Webots R2025a **nightly build 24/11/2026**. The R2025a release
exits at start-up on macOS 27 ("failed to open TCP server in the port range [1234-1244]",
cyberbotics/webots issue 6976, fixed upstream), so the official nightly R2025a build was used.
Controllers ran with Python 3.15; analysis with Python 3.12 (NumPy, Matplotlib).

## Changes to tools/run_experiment.py (see tools/run_experiment.diff)
1. Removed `--minimize`: with it, Webots on macOS 27 hangs before loading the world.
2. Timeout lowered to max(90 s, 0.75 x simulated time): roughly half the headless starts hang
   (controllers never connect); they now fail fast and are retried.
3. Added `--lidar-noise X` (GUIDE exercise 5): inserts `noise X` into the SickLms291 node.

## Commands
    ./run_all_exp7.sh                     # Part A, Part B, exercises 1 and 5 (skips runs already done; re-run to retry failures)
    python exp07-webots/analyse.py ~/webots-work/analysis   # metrics, mean +/- SD, figures

GUI run: worlds/swarm_arena.wbt opened in the Webots window, 120 s -> analysis/trajectories.csv
(Figure 7.2) and the screenshot (Figure 7.1).

## Excluded runs
These CSVs are partial (the run was killed before the full simulated time) and are excluded from all tables and plots:
- pioneer_bubble-0.15_r1 (78 s)
- swarm_cruise-0.2_r1 (41 s)
- swarm_cruise-0.2_r2 (60 s)
- swarm_cruise-0.9_r5 (101 s)
- swarm_cruise-1.0_r1 (57 s)
- swarm_cruise-1.0_r2 (21 s)
- swarm_cruise-1.0_r3 (10 s)

Headless attempts: 59, failed or hung: 31. Headless runs only worked while a normal Webots window was also open.
