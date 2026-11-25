# Experiment 8: Cross-Embodiment Transfer (PyBullet) — run notes

Project: AISR-Cross-Embodiment-PyBullet (course zip), run from a working copy outside this repo.
Only my results, figures and the one script I added are committed here.

Environment: macOS, Apple M5. Python 3.11.16, PyBullet 3.2.7, NumPy 2.4.6, scikit-learn 1.9.1, Matplotlib 3.11.2.
PyBullet 3.2.7 has no macOS arm64 wheel, so pip compiled it from source. On this SDK the bundled
zlib fails to compile (`fdopen` macro clash), fixed with:

    uv venv --python 3.11 .venv
    CFLAGS="-Dfdopen=fdopen" uv pip install --python .venv/bin/python pybullet numpy matplotlib scikit-learn pillow

## Commands run

    python run_all.py                                                  # Parts 0-5 and the side-by-side GIF, default sizes (3 min)
    python experiments/04_learn_once_deploy_many.py --source xarm6     # Exercise E1
    python experiments/e4_scale_sweep.py --episodes 20                 # Exercise E4 (exercises/e4_scale_sweep.py)

Full console output: results/run_all.log, results/e1_source_xarm6.log, results/e4_scale_sweep.log.
All seeds are fixed in the project, so the numbers are reproducible on the same library versions.

## Exercises

- E1: BC policies trained only on xarm6 (60 demos), evaluated on all four robots.
- E4: expert through the task-space interface on the KUKA iiwa at scales 0.6-1.0 (Part 3 layouts, seeds 3000-3019).
