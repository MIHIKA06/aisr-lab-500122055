"""Build a Jupyter notebook from a percent-format script and execute it.

Usage: python tools/build_nb.py exp01-signals/exp01.py
Cells are separated by '# %%'. A cell starting '# %% [markdown]' is markdown;
its lines have the leading '# ' stripped. The notebook is written next to the
script (same name, .ipynb) and executed top to bottom on a fresh kernel.
"""
import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def split_cells(text):
    cells, kind, buf = [], None, []
    for line in text.splitlines():
        if line.startswith('# %%'):
            if kind is not None:
                cells.append((kind, buf))
            kind = 'markdown' if '[markdown]' in line else 'code'
            buf = []
        else:
            buf.append(line)
    if kind is not None:
        cells.append((kind, buf))
    out = []
    for kind, lines in cells:
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip():
            lines.pop(0)
        if kind == 'markdown':
            lines = [l[2:] if l.startswith('# ') else l.lstrip('#') for l in lines]
            out.append(nbformat.v4.new_markdown_cell('\n'.join(lines)))
        else:
            out.append(nbformat.v4.new_code_cell('\n'.join(lines)))
    return out


def main(script):
    script = Path(script).resolve()
    nb = nbformat.v4.new_notebook()
    nb.cells = split_cells(script.read_text())
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    ep = ExecutePreprocessor(timeout=1800, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': str(script.parent)}})
    out = script.with_suffix('.ipynb')
    nbformat.write(nb, out)
    print('wrote', out)


if __name__ == '__main__':
    for s in sys.argv[1:]:
        main(s)
