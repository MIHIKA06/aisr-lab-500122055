"""Experiment 7 analysis: metrics, mean ± SD over repeats, and the report figures.

    python exp07-webots/analyse.py <webots-project>/analysis

Reads runs/<label>_r<N>.csv written by tools/run_experiment.py (columns t, robot, x, y)
and the GUI run trajectories.csv. Metric definitions follow the course analysis/metrics.py:
  path length  metres driven (sum of sample-to-sample distances)
  mean speed   path / duration
  stuck %      share of sample intervals with speed < 1 cm/s
  coverage %   share of grid cells visited by any robot (10 cm swarm, 50 cm Pioneer)
"""
import csv
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'figure.dpi': 110, 'savefig.dpi': 150, 'font.size': 10})
GRID = {'swarm': (0.8, 0.1), 'pioneer': (4.0, 0.5)}     # (arena half-width m, cell m)
HERE = Path(__file__).resolve().parent
FIGS, RES = HERE / 'figs', HERE / 'runs'
FIGS.mkdir(exist_ok=True); RES.mkdir(exist_ok=True)
INCOMPLETE = []


def load(path):
    tracks = defaultdict(list)
    with open(path) as f:
        for r in csv.DictReader(f):
            tracks[r['robot']].append((float(r['t']), float(r['x']), float(r['y'])))
    return {k: np.array(v) for k, v in tracks.items()}


def metrics(tracks, world):
    half, cell = GRID[world]
    n = int(round(2 * half / cell))
    visited, robots = set(), {}
    for name, p in sorted(tracks.items()):
        d = np.hypot(np.diff(p[:, 1]), np.diff(p[:, 2]))
        dt = np.maximum(np.diff(p[:, 0]), 1e-9)
        length = float(d.sum())
        dur = p[-1, 0] - p[0, 0]
        robots[name] = dict(path=length, speed=length / max(dur, 1e-9),
                            stuck=100 * float(np.mean(d / dt < 0.01)))
        for _, x, y in p:
            visited.add((min(n - 1, int((x + half) / cell)), min(n - 1, int((y + half) / cell))))
    return robots, 100 * len(visited) / n**2


def summarise_runs(runs_dir):
    rows = []
    for f in sorted(Path(runs_dir).glob('*_r[0-9].csv')):
        m = re.match(r'(swarm|pioneer)_(.+)_r(\d)$', f.stem)
        if not m:
            continue
        world, setting, rep = m.group(1), m.group(2), int(m.group(3))
        tracks = load(f)
        dur = max(p[-1, 0] for p in tracks.values())
        if dur < 0.98 * {'swarm': 120, 'pioneer': 180}[world]:
            INCOMPLETE.append(f'{f.stem} ({dur:.0f} s)')
            continue
        robots, cov = metrics(tracks, world)
        paths = [r['path'] for r in robots.values()]
        rows.append(dict(world=world, setting=setting, run=rep, coverage=cov,
                         path_mean=float(np.mean(paths)), path_total=float(np.sum(paths)),
                         speed_mean=float(np.mean([r['speed'] for r in robots.values()])),
                         stuck_mean=float(np.mean([r['stuck'] for r in robots.values()])),
                         stuck_worst=float(max(r['stuck'] for r in robots.values())),
                         robots=robots, file=f.name))
    return rows


def agg(rows, world, setting, key):
    v = [r[key] for r in rows if r['world'] == world and r['setting'] == setting]
    return (float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0, len(v))


def plot_tracks(csv_path, world, title, out):
    tracks = load(csv_path)
    half, cell = GRID[world]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5))
    allp = np.vstack([p[:, 1:] for p in tracks.values()])
    for name, p in sorted(tracks.items()):
        a1.plot(p[:, 1], p[:, 2], lw=1, label=name)
        a1.plot(p[0, 1], p[0, 2], 'o', ms=5, color=a1.lines[-1].get_color())
    a1.set(xlim=(-half, half), ylim=(-half, half), aspect='equal',
           xlabel='x (m)', ylabel='y (m)', title='Paths (dot = start)')
    a1.legend(fontsize=8, loc='upper right'); a1.grid(alpha=0.3)
    bins = int(round(2 * half / cell))
    H, _, _ = np.histogram2d(allp[:, 0], allp[:, 1], bins=bins, range=[[-half, half], [-half, half]])
    a2.imshow(H.T > 0, origin='lower', extent=(-half, half, -half, half), cmap='Greens')
    a2.set(aspect='equal', xlabel='x (m)', ylabel='y (m)',
           title=f'Cells visited: {100 * (H > 0).mean():.0f}% of {cell * 100:.0f} cm grid')
    fig.suptitle(title)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


def main(analysis_dir):
    analysis_dir = Path(analysis_dir)
    rows = summarise_runs(analysis_dir / 'runs')
    import shutil
    for f in list((analysis_dir / 'runs').glob('*_r[0-9].csv')) + [analysis_dir / 'trajectories.csv']:
        if f.exists():
            shutil.copy(f, RES / ('gui_' + f.name if f.name == 'trajectories.csv' else f.name))
    with open(RES / 'all_runs.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['world', 'setting', 'run', 'coverage_pct', 'path_mean_m', 'speed_mean_mps',
                    'stuck_mean_pct', 'stuck_worst_pct', 'file'])
        for r in rows:
            w.writerow([r['world'], r['setting'], r['run'], f"{r['coverage']:.1f}", f"{r['path_mean']:.2f}",
                        f"{r['speed_mean']:.3f}", f"{r['stuck_mean']:.1f}", f"{r['stuck_worst']:.1f}", r['file']])
    for r in rows:
        print(f"{r['world']:8s} {r['setting']:14s} r{r['run']}  path/robot {r['path_mean']:6.2f} m  "
              f"speed {r['speed_mean']:.3f} m/s  stuck mean {r['stuck_mean']:5.1f}%  worst {r['stuck_worst']:5.1f}%  "
              f"coverage {r['coverage']:5.1f}%")

    settings = sorted({(r['world'], r['setting']) for r in rows})
    summary = {}
    print('\nExcluded incomplete runs:', INCOMPLETE)
    print('\nMean ± SD per setting')
    for world, s in settings:
        summary[f'{world}:{s}'] = {k: agg(rows, world, s, k) for k in
                                   ('path_mean', 'speed_mean', 'stuck_mean', 'stuck_worst', 'coverage')}
        c, p, st = summary[f'{world}:{s}']['coverage'], summary[f'{world}:{s}']['path_mean'], summary[f'{world}:{s}']['stuck_worst']
        print(f"{world:8s} {s:14s} n={c[2]}  coverage {c[0]:5.1f} ± {c[1]:4.1f}%  path {p[0]:5.2f} ± {p[1]:4.2f} m  "
              f"worst stuck {st[0]:5.1f} ± {st[1]:4.1f}%")
    gui = None
    if (analysis_dir / 'trajectories.csv').exists():
        gr, gcov = metrics(load(analysis_dir / 'trajectories.csv'), 'swarm')
        gui = dict(coverage=gcov, path_mean=float(np.mean([r['path'] for r in gr.values()])),
                   stuck_worst=float(max(r['stuck'] for r in gr.values())))
        print(f"GUI run: coverage {gcov:.1f}%  path/robot {gui['path_mean']:.2f} m  worst stuck {gui['stuck_worst']:.1f}%")
    log = analysis_dir / 'run_all_exp7.log'
    attempts = fails = 0
    for logf in sorted(analysis_dir.glob('run_all_exp7*.log')):
        txt = logf.read_text()
        n_att = txt.count('=== ')
        attempts += n_att
        fails += n_att - txt.count('Trajectory: ')
    json.dump(dict(runs=[{k: v for k, v in r.items()} for r in rows], summary=summary, gui=gui,
                   attempts=attempts, failed=fails, incomplete=INCOMPLETE),
              open(RES / 'summary.json', 'w'), indent=1)

    # Figure 7.2: the GUI run on my screen
    if (analysis_dir / 'trajectories.csv').exists():
        plot_tracks(analysis_dir / 'trajectories.csv', 'swarm',
                    'e-puck swarm, default parameters, 120 s (GUI run)', FIGS / 'fig7_2_swarm_trajectories.png')
    # Figure 7.3: Pioneer default and the bubble = 0.15 failure
    for s, tag in (('default', 'fig7_3_pioneer_default.png'), ('bubble-0.15', 'fig7_3b_pioneer_bubble015.png')):
        f = analysis_dir / 'runs' / f'pioneer_{s}_r1.csv'
        if f.exists():
            plot_tracks(f, 'pioneer', f'Pioneer 3-DX, follow-the-gap, {s}, 180 s, 8 m x 8 m room', FIGS / tag)
    # Swarm cruise=0.9 run with the most-stuck robot
    hi = [r for r in rows if r['setting'] == 'cruise-0.9']
    if hi:
        worst = max(hi, key=lambda r: r['stuck_worst'])
        plot_tracks(analysis_dir / 'runs' / worst['file'], 'swarm',
                    f"e-puck swarm, cruise = 0.9, run {worst['run']}", FIGS / 'fig7_swarm_cruise09_worst.png')

    # Figure 7.4: exercise 1, speed vs safety
    cruises = [0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 1.0]
    pts = [(c, 'default' if c == 0.5 else f'cruise-{c}') for c in cruises]
    pts = [(c, s) for c, s in pts if ('swarm', s) in settings]
    if pts:
        fig, ax = plt.subplots(figsize=(7, 4))
        cov = [agg(rows, 'swarm', s, 'coverage') for _, s in pts]
        stk = [agg(rows, 'swarm', s, 'stuck_worst') for _, s in pts]
        xs = [c for c, _ in pts]
        ax.errorbar(xs, [m for m, _, _ in cov], yerr=[sd for _, sd, _ in cov], fmt='o-', capsize=4,
                    color='tab:green', label='coverage (%)')
        ax.errorbar(xs, [m for m, _, _ in stk], yerr=[sd for _, sd, _ in stk], fmt='s--', capsize=4,
                    color='tab:red', label='worst-robot stuck time (%)')
        ax.set_xlabel('cruise speed parameter (fraction of max wheel speed, 6.28 rad/s)')
        ax.set_ylabel('percentage (%)'); ax.set_ylim(-3, 103); ax.grid(alpha=0.3); ax.legend(fontsize=8)
        ax.set_title('Exercise 1: speed against safety, 120 s runs (mean ± SD over 1–5 complete runs)')
        fig.tight_layout(); fig.savefig(FIGS / 'fig7_4_ex1_speed_vs_safety.png'); plt.close(fig)

    # Exercise 5: lidar noise
    ns = [(0.0, 'default'), (0.001, 'noise-0.001'), (0.003, 'noise-0.003')]
    ns = [(n, s) for n, s in ns if ('pioneer', s) in settings]
    if len(ns) > 1:
        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        x = np.arange(len(ns)); w = 0.38
        for i, (key, lab, col) in enumerate((('coverage', 'coverage (%)', 'tab:green'),
                                             ('stuck_worst', 'stuck time (%)', 'tab:red'))):
            a = [agg(rows, 'pioneer', s, key) for _, s in ns]
            ax.bar(x + (i - 0.5) * w, [m for m, _, _ in a], w, yerr=[sd for _, sd, _ in a], capsize=4,
                   color=col, label=lab)
        ax.set_xticks(x, [f'{n} (≈{n * 80 * 100:.0f} cm)' for n, _ in ns])
        ax.set_xlabel('SICK LMS 291 noise (fraction of 80 m range)'); ax.set_ylabel('percentage (%)')
        ax.set_title('Exercise 5: Pioneer with a noisy lidar, 180 s (mean ± SD)')
        ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)
        fig.tight_layout(); fig.savefig(FIGS / 'fig7_5_ex5_lidar_noise.png'); plt.close(fig)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/Users/mihika/webots-work/analysis')
