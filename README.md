# aisr-lab-500122055

CSAI4014 Algorithms for Intelligent Systems and Robotics — laboratory record.

| | |
|---|---|
| Name | MIHIKA |
| SAP ID | 500122055 |
| Batch | A (B.Tech CSE AI & ML B1), Roll No. R2142230204 |
| Partner(s) | None |

## Layout

Each experiment folder has a percent-format source script (`expNN.py`), the executed
notebook built from it (`expNN.ipynb`), its figures (`figs/`) and the measured values
(`obs.json`). `OBSERVATIONS.md` collects every value used in the report tables.

| Folder | Experiment |
|---|---|
| exp01-signals | 1. Time and frequency domain, and the pendulum |
| exp02-queens | 2. The eight queens problem |
| exp03-search | 3. Breadth-first and depth-first search |
| exp04-hillclimb | 4. Hill climbing |
| exp05-rl | 5. Reinforcement learning (tabular Q-learning) |
| exp06-neural | 6. A simple neural network |
| exp07-webots | 7. Webots reactive swarm and lidar navigation: analysis script, run CSVs, figures, changed runner, NOTES.md |
| exp08-xembody | 8. Cross-embodiment transfer (PyBullet): results, figures, exercise script, NOTES.md |

## Reproduce

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tools/build_nb.py exp0*/exp0*.py   # rebuilds and executes every notebook on a fresh kernel
python tools/summarise.py                 # rewrites OBSERVATIONS.md from the obs.json files
```

## Sources

- CSAI4014 Laboratory Manual, Experiments 1 to 6 (example code adapted from Chapters 2–7).
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed.
- NumPy, SciPy and Matplotlib documentation.

## AI tools

Claude (Anthropic) was used to help write and debug the experiment scripts and plotting code.

## Report

`report/` builds the lab report from the course Word template: `python report/build.py`
(needs LibreOffice for the page-number pass, and the course template saved as `report/template.docx`, which is not included here). `content.py` holds the text and reads every
number from the experiments' `obs.json` / CSV files.

Further sources: Webots and webots-robotics-sim (Exp. 7), AISR-Cross-Embodiment-PyBullet (Exp. 8);
full list in the report's References and Appendix B.
