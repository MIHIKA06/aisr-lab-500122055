"""Exercise E4: find the smallest scaled KUKA that still does the task.

The expert is run through the task-space interface (as in Part 3) on the KUKA
iiwa loaded at several global scales. Only `EMBODIMENTS["kuka_mini"]["scale"]`
is changed between runs; the policy, task and seeds are identical.

    python experiments/e4_scale_sweep.py --episodes 20
"""

import argparse

import _common
import matplotlib.pyplot as plt

from xembody import expert_action
from xembody.robots import EMBODIMENTS
from xembody.rollout import evaluate, print_table, results_path, summarise, write_csv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scales", nargs="+", type=float, default=[0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0])
    ap.add_argument("--episodes", type=int, default=20)
    args = ap.parse_args()

    policy = lambda obs, joints: expert_action(obs)  # noqa: E731
    seeds = [3000 + i for i in range(args.episodes)]   # the Part 3 layouts
    rows = []
    for s in args.scales:
        EMBODIMENTS["kuka_mini"]["scale"] = s
        r = summarise(evaluate("kuka_mini", policy, seeds))
        rows.append(dict(scale=s, **r))
        print(f"  scale {s:.2f}: success {r['success_rate']:.2f}")
    cols = ["scale", "success_rate", "mean_steps", "median_error_cm"]
    print_table(rows, cols, f"E4: expert via task space on KUKA at different scales ({args.episodes} episodes)")
    write_csv(results_path("e4_scale_sweep.csv"), rows, ["scale", "n", *cols[1:]])

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot([r["scale"] for r in rows], [100 * r["success_rate"] for r in rows], "o-",
            color=_common.ROBOT_COLORS["kuka_mini"])
    ax.set_xlabel("KUKA iiwa global scale (1.0 = full size)")
    ax.set_ylabel(f"success rate (%), {args.episodes} episodes")
    ax.set_ylim(-3, 105)
    ax.set_title("Exercise E4: task success against robot scale (task-space expert)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(results_path("e4_scale_sweep.png"), dpi=150)
    print("\nSaved results/e4_scale_sweep.csv/.png")


if __name__ == "__main__":
    main()
