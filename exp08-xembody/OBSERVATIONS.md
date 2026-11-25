# Experiment 8 observations (from results/*.csv)

Table 8.1 Embodiments (Part 1, 3000 random configurations, 90 task points)

| Robot | Arm DOF | Max reach (m) | Task coverage (%) |
|---|---|---|---|
| kuka_iiwa | 7 | 0.94 | 100 |
| franka_panda | 7 | 0.94 | 100 |
| xarm6 | 6 | 0.76 | 100 |
| kuka_mini | 7 | 0.66 | 48 |

Table 8.2 Joint-space replay of KUKA trajectories (Part 2, 10 episodes)

| Robot | Success | Mean path deviation (cm) | Median cube-goal error (cm) |
|---|---|---|---|
| kuka_iiwa (itself) | 100% | 1.4 | 0.05 |
| franka_panda | 0% | 16.7 | 29.2 |
| xarm6 | 0% | 27.2 | 34.3 |
| kuka_mini | 0% | 17.6 | 34.3 |

Table 8.3 Task-space transfer of the expert (Part 3, 20 episodes)

| Robot | Success | Mean steps | Median cube-goal error (cm) |
|---|---|---|---|
| kuka_iiwa | 100% | 50.5 | 0.15 |
| franka_panda | 100% | 46.6 | 0.13 |
| xarm6 | 100% | 44.9 | 0.27 |
| kuka_mini | 30% | 43.8 | 1.54 |

Table 8.4 Learn on KUKA, deploy everywhere (Part 4, 60 demos — 59/60 expert successes, 3893 pairs; 20 test episodes)

| Robot | Expert | BC-agnostic | BC-proprio |
|---|---|---|---|
| kuka_iiwa (source) | 100% | 100% | 100% |
| franka_panda | 100% | 100% | 0% |
| xarm6 | 100% | 100% | 0% |
| kuka_mini | 50% | 55% | 0% |

Table 8.5 Leave-one-embodiment-out (Part 5, 60 demos total, 20 episodes on the unseen robot)

| Unseen robot | single, agnostic | multi, agnostic | single, proprio | multi, proprio |
|---|---|---|---|---|
| kuka_iiwa | 100% (franka) | 100% (franka+xarm6) | 0% | 0% |
| franka_panda | 100% (kuka) | 100% (kuka+xarm6) | 0% | 5% |
| xarm6 | 100% (kuka) | 100% (kuka+franka) | 0% | 0% |

Side-by-side demo (BC-agnostic, 3 episodes): kuka_iiwa 3/3, franka_panda 3/3, xarm6 3/3, kuka_mini 2/3.

Exercise E1 (source = xarm6, 20 episodes): expert / BC-agnostic / BC-proprio
kuka_iiwa 100/100/0, franka_panda 100/95/0, xarm6 (source) 100/100/100, kuka_mini 50/55/0 (%).

Exercise E4 (task-space expert on scaled KUKA, 20 episodes):

| Scale | 0.60 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|
| Success | 0% | 30% | 75% | 95% | 100% | 100% | 100% |
| Median error (cm) | 29.1 | 1.54 | 0.30 | 0.16 | 0.15 | 0.14 | 0.15 |
