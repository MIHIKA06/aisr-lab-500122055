"""Text, tables and figures of the AISR laboratory report.

Numbers are read from each experiment's obs.json / result CSVs so the report always
matches the runs in the repository. [[...]] marks a personal detail still to be filled.
"""
import csv
import json
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent

PERSON = dict(
    name='MIHIKA',
    sap='500122055',
    roll='R2142230204',
    batch='A (B.Tech CSE AI & ML B1)',
    batch_letter='A',
    partner='None',
    github='https://github.com/MIHIKA06/aisr-lab-500122055',
    submission_date='25 November 2026',
)
PARTNER = PERSON['partner']
RUN_DATE = '25/11/2026'

SUBHEADINGS = ['Aim', 'Objectives', 'Software and Apparatus', 'Theory', 'Procedure', 'Program / Code',
               'Observations', 'Results', 'Discussion', 'Questions', 'Conclusion']

SW = 'Python 3.12.16, NumPy 2.5.5, SciPy 1.18.1, Matplotlib 3.11.2, JupyterLab; macOS 27 on an Apple M5 laptop. No hardware.'


def J(path):
    return json.loads((LAB / path).read_text())


def header(session):
    return f'Date performed: {RUN_DATE}     Session: {session}     Partner: {PARTNER}'


def code_of(path, start, end):
    lines = (LAB / path).read_text().split('\n')
    return '\n'.join(lines[start - 1:end])


def find_lines(path, first, last):
    """Return the source between the line starting with `first` and the line starting with `last` (inclusive)."""
    lines = (LAB / path).read_text().split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith(first))
    j = next(k for k, l in enumerate(lines) if k >= i and l.startswith(last))
    return '\n'.join(lines[i:j + 1])


# --------------------------------------------------------------------------- Experiment 1
o1 = J('exp01-signals/obs.json')
s1 = o1['sampling']
lk = o1['leakage']['peaks']
E1 = dict(
    n=1, title='Time and Frequency Domain, and the Pendulum', source='Lab Manual, Chapter 2',
    header_line=header('1'),
    aim='To represent a sampled signal in the time domain and in the frequency domain using the discrete Fourier '
        'transform, and to simulate the motion of a simple pendulum by numerical integration of its equation of motion.',
    objectives=[
        'Build a sampled test signal whose components are known, and state its sampling rate, record length, number of samples and frequency resolution.',
        'Compute a one-sided amplitude spectrum scaled so that the peak heights read directly in the units of the signal.',
        'Predict where an undersampled sine will appear, then show it, to see aliasing happen.',
        'Rewrite the pendulum’s second-order equation as a first-order system, integrate it with SciPy and compare three damping levels.',
        'Read energy behaviour from a phase portrait and measure how the period depends on the starting amplitude.',
    ],
    software=SW + ' Numerical integration with scipy.integrate.solve_ivp (RK45) [1]–[3].',
    theory=[
        'A continuous signal is stored as N samples taken every Δt seconds, so the sampling rate is fs = 1/Δt and the record '
        'length is T = NΔt. Two numbers then fix how a spectrum can be read: the bin spacing (frequency resolution) '
        'Δf = fs/N = 1/T, which depends only on how long we record, and the Nyquist limit fmax = fs/2, which depends only on '
        'how fast we sample [4], [5]. For a real signal the FFT returns N/2 + 1 useful bins (rfft); multiplying the magnitude by '
        '2/N (and the DC bin by 1/N) makes each peak equal to the amplitude of the sinusoid that produced it. If a '
        'component does not fit a whole number of cycles in T it falls between bins and its energy spreads into its '
        'neighbours; this is spectral leakage.',
        'A component above fs/2 is not lost; it folds back about the Nyquist limit and appears at |fs − f| (more generally '
        'at |f − k·fs| for the nearest integer k). After sampling, the alias cannot be told apart from a real component at '
        'that frequency, so aliasing must be prevented before sampling with an analogue low-pass filter [5].',
        'For a pendulum of length L with viscous damping coefficient b (per unit mass, s⁻¹), the angle θ from the vertical '
        'obeys θ̈ + b θ̇ + (g/L) sin θ = 0. Integrators accept only first-order systems, so the state y = (θ, ω) with ω = θ̇ '
        'gives dθ/dt = ω and dω/dt = −bω − (g/L) sin θ. For small angles sin θ ≈ θ and the motion is simple harmonic with '
        'period T0 = 2π√(L/g), independent of amplitude. The real (non-linear) pendulum has a longer period that grows '
        'with amplitude and tends to infinity as the release angle approaches 180°, where the bob starts at the unstable '
        'upright equilibrium [4]. With b = 0 the energy E = ½ω² − (g/L) cos θ is conserved, so phase-plane trajectories are '
        'closed curves; with b > 0 energy is lost and trajectories spiral into the origin.',
    ],
    procedure=[
        f'Chose fs = {s1["fs"]:.0f} Hz and T = {s1["T"]} s, built t = np.arange(0, T, 1/fs) and recorded N = {s1["N"]}, '
        f'Δf = {s1["df"]} Hz and fs/2 = {s1["nyquist"]:.0f} Hz (Table 1.1).',
        'Built x(t) = 1.00 sin(2π·5t) + 0.50 sin(2π·20t) + 0.25 sin(2π·50t) plus Gaussian noise (σ = 0.2, generator seed 0) '
        'and plotted the first 0.5 s (Figure 1.1).',
        'Computed the one-sided spectrum with np.fft.rfft and np.fft.rfftfreq, scaled it by 2/N, and read the peak frequency '
        'and height near each set frequency (Figure 1.2, Table 1.2).',
        'Repeated the spectrum with T = 1.7 s to look at spectral leakage (Figure 1.6).',
        'Sampled a single 5 Hz sine at fs = 8 Hz for 1 s and located the peak of its spectrum (Figure 1.3).',
        'Integrated the pendulum (L = 1 m, g = 9.81 m/s²) with solve_ivp, rtol = 1e-9, atol = 1e-12, from 40° at rest for '
        'b = 0, 0.3 and 2.0 s⁻¹, and plotted θ(t) and the phase portrait (Figures 1.4 and 1.5).',
        'For b = 0, integrated 60 s records (dt = 5 ms) from 5° to 175° and measured the period twice: from the mean spacing of '
        'interpolated upward zero crossings and from the highest non-DC spectral peak (Table 1.3, Figure 1.5 right).',
        'Ran the whole notebook top to bottom on a fresh kernel (python tools/build_nb.py exp01-signals/exp01.py).',
    ],
    code_intro='Key part of the program (full notebook: exp01-signals/exp01.ipynb):',
    code=find_lines('exp01-signals/exp01.py', 'def amplitude_spectrum', '    return f, amp') + '\n\n' +
         find_lines('exp01-signals/exp01.py', 'def pendulum', '    return sol.t') + '\n\n' +
         find_lines('exp01-signals/exp01.py', 'def period_zero_crossings', '    return float(np.mean'),
    observations=[
        ('table', ('Table 1.1', 'Sampling parameters used'), ['Quantity', 'Symbol', 'Value', 'Unit'], [
            ['Sampling rate', 'fs', f'{s1["fs"]:.0f}', 'Hz'], ['Record length', 'T', f'{s1["T"]}', 's'],
            ['Number of samples', 'N', f'{s1["N"]}', '–'], ['Frequency resolution', 'Δf = fs/N', f'{s1["df"]}', 'Hz'],
            ['Nyquist limit', 'fs/2', f'{s1["nyquist"]:.1f}', 'Hz']], [2.2, 1.4, 1, 0.8]),
        ('table', ('Table 1.2', 'Spectrum of the constructed signal: set and measured values'),
         ['Component', 'Set (Hz)', 'Measured (Hz)', 'Set amplitude', 'Measured amplitude'],
         [[nm, f'{a}', f'{b:.1f}', f'{c:.2f}', f'{d:.2f}'] for nm, (a, b, c, d) in zip(['First', 'Second', 'Third'], o1['spectrum'])]),
        ('table', ('Table 1.3', 'Measured period against initial amplitude (undamped)'),
         ['Initial angle (deg)', 'Period by zero crossings (s)', 'Period by spectrum (s)', 'Ratio to T0'],
         [[f'{a}', f'{tz:.3f}', f'{ts:.3f}', f'{r:.2f}'] for a, tz, ts, r in o1['period_table']]),
        ('para', f'Other observations: the 5 Hz sine sampled at 8 Hz shows its peak at {o1["alias_peak_hz"]:.1f} Hz; '
                 f'T0 = 2π√(L/g) = {o1["T0"]:.4f} s for L = 1 m, g = 9.81 m/s²; damping coefficients used b = 0, 0.3 and 2.0 s⁻¹. '
                 f'With T = 1.7 s (Δf = {o1["leakage"]["df"]:.3f} Hz) the 5 Hz peak moved to the nearest bin, '
                 f'{lk[0][1]:.3f} Hz, and its height fell from 1.01 to {lk[0][3]:.2f}, while the 20 Hz and 50 Hz peaks kept '
                 f'heights {lk[1][3]:.2f} and {lk[2][3]:.2f}.'),
    ],
    results=[
        ('fig', LAB / 'exp01-signals/figs/fig1_1_time_signal.png', ('Figure 1.1', 'Constructed signal in the time domain'), 14.5),
        ('fig', LAB / 'exp01-signals/figs/fig1_2_spectrum.png', ('Figure 1.2', 'One-sided amplitude spectrum with labelled peaks'), 14.5),
        ('fig', LAB / 'exp01-signals/figs/fig1_3_aliasing.png', ('Figure 1.3', 'Aliasing: 5 Hz sine sampled at 8 Hz'), 15),
        ('fig', LAB / 'exp01-signals/figs/fig1_4_pendulum_damping.png', ('Figure 1.4', 'Pendulum angle against time for three damping values'), 14.5),
        ('fig', LAB / 'exp01-signals/figs/fig1_5_phase_and_period.png', ('Figure 1.5', 'Phase portrait (left) and period against initial amplitude (right)'), 15),
        ('fig', LAB / 'exp01-signals/figs/fig1_6_leakage.png', ('Figure 1.6', 'Spectral leakage: the same signal recorded for T = 2.0 s and T = 1.7 s'), 14.5),
        ('para', 'The three components were recovered at exactly 5.0, 20.0 and 50.0 Hz with amplitudes 1.01, 0.49 and 0.25 '
                 '(Table 1.2, Figure 1.2), even though none of them can be seen in the noisy time trace (Figure 1.1). The '
                 'undersampled 5 Hz sine appeared at 3.0 Hz = |8 − 5| Hz (Figure 1.3). Damping changed the decay as expected '
                 '(Figure 1.4) and the undamped orbit is closed while the damped ones spiral inward (Figure 1.5, left). The '
                 'period rose from 2.007 s at 5° (ratio 1.00) to 5.773 s at 175° (ratio 2.88) (Table 1.3).'),
    ],
    discussion=[
        'I expected the peaks to land exactly on the set frequencies, and they did, because with T = 2 s every component '
        'completes a whole number of cycles and sits on a bin. The measured amplitudes differ from the set ones by at most '
        '0.01 because the seeded noise adds a small random contribution to every bin.',
        'The leakage run was more interesting than I expected. With T = 1.7 s only the 5 Hz component leaked: 5 × 1.7 = 8.5 '
        'cycles is not a whole number, so its energy spread over neighbouring bins and the tallest bin dropped to 0.66. But '
        '20 × 1.7 = 34 and 50 × 1.7 = 85 cycles are whole numbers, so those two still fell exactly on bins (20.000 and '
        '50.000 Hz) and kept their heights. Leakage is about whole cycles in the record, not about T itself.',
        'For the pendulum the small-angle prediction T0 = 2.006 s held at 5°, but the two period measurements disagree with each '
        'other in a way that is an artefact, not physics. The spectral method can only return 1/(k·Δf) with Δf = 1/60 Hz, so '
        'it gives 2.000 s at 5° (true value about 2.007 s), and at 175° it gives 6.001 s against 5.773 s by zero crossings: '
        'the bins near 0.17 Hz are 0.017 Hz apart, about 10% of the frequency. The zero-crossing value, which interpolates '
        'between samples, is the better estimate. The growth of the period with amplitude, slow at first and then very '
        'steep near 180°, is the real non-linear effect the small-angle model leaves out.',
    ],
    answers=[
        'From one record alone I cannot be sure: at fs = 500 Hz any component at k·500 ± 5 Hz would also land at 5 Hz. A 45 Hz '
        'component, though, is below the 250 Hz Nyquist limit, so it would appear at 45 Hz and not fold. A peak at 5 Hz could '
        'only be an alias of something at 495 Hz, 505 Hz, and so on. To rule that out I would use an anti-aliasing low-pass filter '
        'before sampling, or sample again at a different fs: a real 5 Hz peak stays at 5 Hz, while an alias moves.',
        'The resolution is Δf = fs/N = 1/T, so it is set only by the record length. Sampling faster raises fs but also raises N for '
        'the same T, so their ratio does not change. Faster sampling only raises the Nyquist limit fs/2. For finer resolution I must '
        'record for longer (for example, the 60 s pendulum record gives Δf = 0.0167 Hz).',
        'solve_ivp always calls the derivative as f(t, y). If I wrote f(y, t) (the odeint order), the time value would be unpacked as '
        'the state and the state array as time, so the code would either crash or silently integrate the wrong equation. The order '
        'of the parameters has to match how the solver calls the function.',
        'For the undamped pendulum, a closed orbit is a curve of constant energy, so a larger orbit means more energy. The enclosed '
        'area ∮ω dθ is the action of the motion, and dA/dE equals the period. An orbit that encloses more area therefore carries more '
        'energy and, for the pendulum, takes longer to go round, which matches Table 1.3.',
        'At 180° the bob would be balanced upright, an unstable equilibrium where the restoring torque (g/L)·sin θ is zero. Started '
        'near it, the pendulum spends a very long time creeping away from the top on each swing because the torque there is almost '
        'zero. The period integral 4∫dθ/ω grows like a logarithm and tends to infinity as θ0 → 180°. That is the steep rise at the '
        'right of Figure 1.5, from 3.07 s at 135° to 5.77 s at 175°.',
    ],
    conclusion='The FFT recovered the frequencies and amplitudes of a noisy three-tone signal, and an undersampled 5 Hz sine '
               'appeared at the predicted 3 Hz alias. Spectral leakage happened only for the component that did not fit '
               'whole cycles in the record. The integrated pendulum showed energy conservation without damping and a period '
               'that grows from 1.00·T0 to 2.88·T0 with amplitude. The same tools are used on robots to set encoder and IMU '
               'sampling rates, to diagnose vibration, and to model and simulate joints before a controller is designed.',
)

# --------------------------------------------------------------------------- Experiment 2
o2 = J('exp02-queens/obs.json')
r2 = {r['n']: r for r in o2['rows']}
def fmt_t(x):
    return f'{x:.4f}' if x >= 1e-3 else f'{x * 1e6:.0f} µs'
E2 = dict(
    n=2, title='The Eight Queens Problem', source='Lab Manual, Chapter 3', header_line=header('2'),
    aim='To formulate the eight queens problem as a constraint satisfaction problem, to solve it by generate-and-test and '
        'by backtracking, and to measure the effect that the choice of representation and of search strategy has on the '
        'cost of the solution.',
    objectives=[
        'Write eight queens as variables, domains and constraints, and choose an encoding that removes conflicts by construction.',
        'Solve it by generate-and-test over permutations and time it.',
        'Solve it by recursive backtracking that checks only the columns already filled, and count the nodes visited.',
        'Check that both methods give the same solutions, then compare their cost for n = 4 to 10.',
        'Reduce the 92 solutions to the fundamental ones under the symmetries of the board.',
    ],
    software=SW + ' Only the standard library (itertools, time) is needed for the solvers; Matplotlib draws the board and the timing plot [3].',
    theory=[
        'A constraint satisfaction problem (CSP) has variables, a domain for each variable and constraints between them [6]. '
        'The cost of solving it depends heavily on the encoding. Taking eight queens as variables with all 64 squares as the '
        'domain gives C(64, 8) = 4 426 165 368 placements. Making the columns the variables, with the row of the queen as the '
        'value (board[c] = row), makes two queens in one column impossible and leaves 8⁸ = 16 777 216 boards. Requiring the '
        'rows to be a permutation of 0…7 also rules out shared rows and leaves 8! = 40 320 candidates. Diagonals are never removed '
        'by the encoding: queens in columns i and j attack each other diagonally exactly when |r_i − r_j| = |i − j|.',
        'Generate-and-test enumerates every candidate and keeps those with zero conflicts. It is obviously correct but always '
        'does the full n! work. Backtracking builds a solution one column at a time and tests a new queen only against the queens '
        'already placed to its left. As soon as a placement is unsafe, the whole subtree below it is pruned. After exploring a '
        'branch it undoes the placement before trying the next row. It is still exponential in the worst case, but pruning removes '
        'most of the tree [4], [6].',
        'The square board has eight symmetries (four rotations, each with or without a reflection). Solutions related by a '
        'symmetry are the same up to how the board is turned, so the 92 solutions for n = 8 fall into 12 symmetry classes.',
    ],
    procedure=[
        'Wrote conflicts(board), which counts attacking pairs for a board given as one row index per column.',
        'Kept the permutations of range(8) with zero conflicts (generate-and-test) and timed it with time.perf_counter.',
        'Wrote is_safe(board, col, row), which checks only columns 0…col−1, and a recursive place() that sets board[col] = row, '
        'recurses, then resets board[col] = −1. Counted every (column, row) tried as a node.',
        'Asserted that both methods return the same set of solutions for n = 8, and drew the first solution found (Figure 2.1).',
        'Repeated both methods for n = 4…10, recording solutions, nodes and run time (Table 2.1, Figure 2.2).',
        'Generated the 8 symmetric images of every n = 8 solution and counted the distinct canonical forms.',
    ],
    code_intro='Key part of the program (full notebook: exp02-queens/exp02.ipynb):',
    code=find_lines('exp02-queens/exp02.py', 'def conflicts', '    return [p for p in permutations') + '\n\n' +
         find_lines('exp02-queens/exp02.py', 'def is_safe', '    return sols, nodes[0]'),
    observations=[
        ('table', ('Table 2.1', 'Solutions, nodes visited and run time for n = 4 to 10'),
         ['n', 'Solutions', 'Nodes visited', 'Backtracking (s)', 'Generate and test (s)'],
         [[str(n), str(r2[n]['solutions']), f"{r2[n]['nodes']:,}".replace(',', ' '), fmt_t(r2[n]['t_bt']), fmt_t(r2[n]['t_gt'])]
          for n in range(4, 11)]),
        ('para', f'Both methods returned identical solution counts for every n (the notebook asserts this). First solution found '
                 f'for n = 8, as row per column: {tuple(o2["first_solution"])}. Distinct solutions under the 8 board symmetries: '
                 f'{o2["fundamental"]}. Timings measured on an {o2["cpu"]} (macOS 27), Python {o2["python"]}, single run each.'),
    ],
    results=[
        ('fig', LAB / 'exp02-queens/figs/fig2_1_first_solution.png', ('Figure 2.1', 'First solution found for n = 8, drawn as a board'), 9),
        ('fig', LAB / 'exp02-queens/figs/fig2_2_runtime.png', ('Figure 2.2', 'Run time against board size n (log scale), both methods'), 12.5),
        ('para', f"Both methods found 92 solutions for n = 8. Backtracking visited {r2[8]['nodes']:,} nodes and took "
                 f"{r2[8]['t_bt'] * 1000:.1f} ms, against {r2[8]['t_gt'] * 1000:.1f} ms for generate-and-test (Table 2.1). By n = 10 the "
                 f"times were {r2[10]['t_bt']:.3f} s against {r2[10]['t_gt']:.2f} s, a factor of about {r2[10]['t_gt'] / r2[10]['t_bt']:.0f}. "
                 f"On the log axis of Figure 2.2 both curves are close to straight lines, with generate-and-test the steeper one."
                 .replace(',', ' ')),
    ],
    discussion=[
        'I expected backtracking to win and the gap to grow with n, and it did. Generate-and-test grows like n!·n² (every '
        'permutation, with an O(n²) conflict check), while backtracking’s node count grew by a factor of about 4.5–4.8 per extra '
        'column (15 720 → 72 378 → 348 150). The ratio of run times went from about 1.3 at n = 4 to about 23 at n = 8 and 126 at '
        'n = 10.',
        'The manual reports a factor of about 70 at n = 10; mine is larger (126). My times are faster overall on this M5, and the '
        'ratio differs because the two methods stress different parts of the interpreter (deep recursion against tight tuple '
        'loops). The node counts are machine-independent and match the manual exactly, so the pattern is the same. At n = 4 and 5 '
        'the times are a few microseconds and mostly timer overhead, so I do not read anything into their ratio.',
        'The solution counts (2, 10, 4, 40, 92, 352, 724) agree for the two methods, which is the real check that the faster '
        'method is not simply missing solutions. Note that n = 6 has fewer solutions than n = 5, so the count is not monotone in n.',
    ],
    answers=[
        'One row index per column means each column holds exactly one queen, so two queens can never share a column. With a '
        'general list of eight row indices, two queens can still share a row (board[i] == board[j]) and diagonals are never excluded '
        '(|board[i] − board[j]| == |i − j|). Using permutations also removes row conflicts, leaving only the diagonal test.',
        'The diagonal test in is_safe. I tried it: writing (board[c] − row) == abs(c − col), with the abs dropped on the left, gives '
        'exactly 2113 solutions for n = 8. Since c < col, the right side is always positive, so only queens on one diagonal '
        'direction are detected and boards with attacks on the other diagonal are accepted. Restoring abs() on board[c] − row gives 92.',
        'is_safe is called while column col is being filled, and only columns 0…col−1 contain queens; the columns to the right '
        'are still empty (−1), so they cannot attack. Checking them would be wasted work and, with −1 entries, could even give '
        'false conflicts.',
        'Because it prunes. A conflict found at column k removes the entire subtree of n^(n−k) completions at once, so the '
        'search visits only 15 720 nodes for n = 8 instead of enumerating 40 320 permutations, and the gap widens with n. The '
        'exponential worst case does not happen on this problem, and it also finds all solutions, which local search cannot promise.',
        'The board has 8 symmetries (4 rotations × reflection), so each fundamental solution generates up to 8 distinct boards. '
        'Eleven of the 12 fundamental solutions give 8 images each (88) but one is symmetric under a 180° rotation, so it has only '
        '4 distinct images: 88 + 4 = 92. My program confirmed 12 canonical forms.',
    ],
    conclusion='Encoding the board as one row per column removed column conflicts by construction, and backtracking with an '
               'undo step found all 92 solutions after only 15 720 nodes. It beat generate-and-test by a factor that grew '
               'from about 1 at n = 4 to over 100 at n = 10. The same CSP formulation and pruning are used for task '
               'allocation across robot fleets, timetabling, register allocation and frequency assignment.',
)

# --------------------------------------------------------------------------- Experiment 3
o3 = J('exp03-search/obs.json')
b3, d3 = o3['results']['bfs'], o3['results']['dfs']
E3 = dict(
    n=3, title='Breadth-First and Depth-First Search', source='Lab Manual, Chapter 4', header_line=header('3'),
    aim='To represent a maze as an implicit graph, to implement breadth-first and depth-first search as one function '
        'differing in a single line, and to compare them on the number of cells expanded and the length of the path returned.',
    objectives=[
        'Generate a maze that is guaranteed to have a path, and treat its open cells as an implicit graph whose edges are computed on demand.',
        'Implement one search function with a frontier, an explored set and a parent map, where a single line selects BFS or DFS.',
        'Reconstruct the path from the parent map and check that every step is adjacent and on an open cell.',
        'Measure and explain the trade-off between cells expanded, frontier size and path length.',
    ],
    software=SW + ' collections.deque provides the frontier.',
    theory=[
        'A search problem consists of a state space, a start state, a goal test and a successor function [6]. Graph search keeps '
        'a frontier of discovered but unexpanded states and a record of states already reached. Breadth-first search (BFS) takes '
        'the oldest state from the frontier (FIFO queue), so it expands states in order of depth. With unit step costs, the first '
        'time it reaches the goal it has found a shortest path. It is complete and optimal, but the frontier can hold a whole '
        'depth layer: O(b^d) memory for branching factor b and solution depth d.',
        'Depth-first search (DFS) takes the newest state (LIFO stack). It follows one corridor to its end before backing up, '
        'so it returns whichever path it reaches the goal by first, with no guarantee of optimality. Its memory is O(b·m) for '
        'maximum depth m. With a deque the two algorithms differ only in popleft() versus pop().',
        'The maze is carved by randomised depth-first search on a grid of rooms (odd coordinates), which produces a perfect '
        'maze. I then knocked out about 8% of eligible walls to add some loops, so that more than one route exists and the BFS '
        'optimality guarantee actually matters. Neighbours are generated on demand by checking bounds first and then whether the '
        'cell is open.',
    ],
    procedure=[
        f'Carved a {o3["H"]} × {o3["W"]} maze (seed 7) with {o3["open_cells"]} open cells; start (1, 1), goal ({o3["H"] - 2}, {o3["W"] - 2}).',
        'Wrote neighbours(cell), which yields the up/down/left/right cells that are inside the grid and open (bounds tested first).',
        'Wrote search(start, goal, mode), which pops from the left for BFS and from the right for DFS, marks a cell in the parent '
        'map when it is enqueued, records the expansion order and the frontier size at every expansion, and stops at the goal.',
        'Rebuilt the path by following parent links back from the goal and reversing them, then validated adjacency and walls.',
        'Plotted both searches shaded by expansion order with the path overlaid (Figure 3.1), and the frontier size per step (Figure 3.2).',
    ],
    code_intro='Key part of the program (full notebook: exp03-search/exp03.ipynb):',
    code=find_lines('exp03-search/exp03.py', 'def neighbours', '                yield (nr, nc)') + '\n\n' +
         find_lines('exp03-search/exp03.py', 'def search', '    return order, path[::-1], frontier_size'),
    observations=[
        ('table', ('Table 3.1', 'BFS and DFS on the same maze'), ['Quantity', 'BFS', 'DFS'], [
            ['Maze size (rows × cols)', f'{o3["H"]} × {o3["W"]}', f'{o3["H"]} × {o3["W"]}'],
            ['Number of open cells', str(o3['open_cells']), str(o3['open_cells'])],
            ['Cells expanded', str(b3['expanded']), str(d3['expanded'])],
            ['Path length (steps)', str(b3['path_steps']), str(d3['path_steps'])],
            ['Maximum frontier size (cells)', str(b3['max_frontier']), str(d3['max_frontier'])],
            ['Path validated (adjacent and clear of walls)', 'Yes' if b3['valid'] else 'No', 'Yes' if d3['valid'] else 'No']],
         [2.6, 1, 1]),
    ],
    results=[
        ('fig', LAB / 'exp03-search/figs/fig3_1_maze_paths.png', ('Figure 3.1', 'Maze with the BFS path (top) and the DFS path (bottom), shaded by expansion order'), 11.5),
        ('fig', LAB / 'exp03-search/figs/fig3_2_frontier.png', ('Figure 3.2', 'Frontier size against expansion step for BFS and DFS'), 13),
        ('para', f'BFS expanded all {b3["expanded"]} open cells and returned a {b3["path_steps"]}-step path; DFS expanded '
                 f'{d3["expanded"]} cells and returned a {d3["path_steps"]}-step path, {100 * (d3["path_steps"] / b3["path_steps"] - 1):.0f}% '
                 f'longer (Table 3.1). Both paths passed validation. In Figure 3.1 BFS shading spreads out evenly from the start, '
                 f'while DFS runs down single corridors and leaves the right half of the maze unexplored.'),
    ],
    discussion=[
        'I expected BFS to find the shortest path and to expand more cells, and DFS to be cheaper but give a longer path. That is '
        'what happened, but more strongly than in the manual: in my maze the goal is the cell farthest from the start, so BFS had '
        'to expand every open cell (395 of 395) before reaching it. DFS happened to choose corridors that led towards the goal '
        'and stopped after 222 expansions, but its route is 114 steps against the optimal 64.',
        'These numbers depend on this particular maze and where the goal is. Placing the goal near the start would have made BFS '
        'cheap, and a different corridor choice could make DFS expand almost the whole maze. What does not depend on the maze is '
        'that the BFS path is guaranteed to be a shortest one.',
        'The frontier sizes (Figure 3.2) were similar for the two methods here (maximum 16 against 15 cells), not the large '
        'difference the theory suggests. A maze is a nearly tree-like graph with a branching factor close to 1, so BFS layers stay '
        'narrow. The O(b^d) memory cost of BFS shows up on open grids, not in corridors.',
    ],
    answers=[
        f'In my run the paths were {d3["path_steps"]} (DFS) and {b3["path_steps"]} (BFS) steps. I can conclude that BFS found a shortest '
        'path, because with unit costs it expands states in order of depth, and that the DFS path is longer than necessary. I '
        'cannot conclude that DFS is generally worse at expansions, or that the ratio of path lengths holds for other mazes; both '
        'depend on the maze and the goal position.',
        'If the wall check comes first, maze[nr, nc] is read before we know the index is valid. With Python/NumPy a negative '
        'index such as −1 does not fail; it silently wraps to the last row or column. The search would then step through the '
        'outer wall onto the far side of the grid without raising any error.',
        'If cells were marked only when expanded, the same cell could be added to the frontier many times, once from each '
        'neighbour that reaches it before it is expanded. This wastes memory and time and, for DFS, can overwrite the parent '
        'link. Marking on enqueue makes each cell enter the frontier once and fixes its parent the first time it is discovered.',
        'BFS stores a whole layer of the search: O(b^d) space. DFS stores the current path plus the unexpanded siblings: O(b·m). '
        'On a memory-constrained robot I would use DFS, or better, iterative deepening DFS, which keeps DFS memory but returns '
        'the shortest path like BFS.',
        'Yes, if every move (including diagonal) counts as one step, because BFS minimises the number of moves. If diagonal moves '
        'have their real length √2 the costs are no longer equal, so BFS may return a path with fewer but longer moves. Then '
        'uniform-cost search or A* is needed to get the shortest distance.',
    ],
    conclusion='One search function with a single changed line gave two algorithms. BFS returned the shortest path '
               f'({b3["path_steps"]} steps) but expanded every open cell, while DFS expanded {d3["expanded"]} cells and '
               f'returned a {d3["path_steps"]}-step path. Optimality is a guarantee of BFS, while cost depends on the maze. '
               'These are the base cases of the grid planners (wavefront, Dijkstra, A*) used on robot occupancy grids.',
)

# --------------------------------------------------------------------------- Experiment 4
o4 = J('exp04-hillclimb/obs.json')
p4 = o4['p']
E4 = dict(
    n=4, title='Hill Climbing', source='Lab Manual, Chapter 5', header_line=header('3'),
    aim='To implement hill climbing as a local search, to observe its failure on local optima, plateaus and ridges, and to '
        'measure the improvement obtained from random restarts.',
    objectives=[
        'Contrast local search (one current state) with systematic search (a frontier of states).',
        'Implement steepest-ascent hill climbing on a 1-D landscape and on eight queens (minimising conflicts).',
        'Measure the success rate of a single climb and show how random restarts raise it.',
        'Compare the measured restart curve with the independent-trials prediction 1 − (1 − p)^k.',
    ],
    software=SW + ' The conflict counter from Experiment 2 is reused; scipy.signal.argrelextrema marks local maxima.',
    theory=[
        'Systematic search keeps many candidate states and is complete; local search keeps one complete state and moves to a '
        'better neighbour, so memory is constant but completeness is lost [6]. Steepest-ascent hill climbing evaluates every '
        'neighbour and moves to the best, stopping when none is better. For eight queens a state is a full board (one queen '
        'per column), a neighbour moves one queen within its column (8 × 7 = 56 neighbours), and the objective h is the number '
        'of attacking pairs, minimised to 0.',
        'It gets stuck in three ways. At a local optimum every neighbour is worse, but the state is not the global best. On a '
        'plateau neighbours are equal, so there is no slope to follow (a shoulder can be crossed with sideways moves; a flat '
        'optimum cannot). On a ridge, improvement needs a combined move that no single step offers.',
        'Random restarts repeat the climb from fresh random states. If one climb succeeds with probability p and climbs are '
        'independent, at least one of k succeeds with probability P(k) = 1 − (1 − p)^k. The number of restarts for 99% success '
        'is k = ⌈ln 0.01 / ln(1 − p)⌉ [6].',
    ],
    procedure=[
        'Plotted f(x) = sin x + 0.6 sin 2.7x + 0.35 sin 5.1x − 0.05(x − 5)² on [0, 10], marked its local maxima, and ran a 1-D '
        'climber from 25 evenly spaced starts (Figure 4.1).',
        f'Implemented hill_climb(n, seed, sideways): a random complete board, then repeated best single-queen moves until h = 0 '
        f'(success) or no improving move (failure). Ran {o4["trials"]} seeds, then {o4["trials"]} different seeds (Table 4.1).',
        f'Wrapped it in hill_climb_restarts for k = 1, 2, 5, 10 and 20, with {o4["trials"]} trials each, and compared with '
        f'1 − (1 − p)^k using p from step 2 (Table 4.2, Figure 4.2).',
        'As an extra check for question 1, allowed up to 100 sideways (equal-cost) moves and re-measured the success rate.',
    ],
    code_intro='Key part of the program (full notebook: exp04-hillclimb/exp04.ipynb):',
    code=find_lines('exp04-hillclimb/exp04.py', 'def hill_climb(', '        board[c] = row') + '\n\n' +
         find_lines('exp04-hillclimb/exp04.py', 'def hill_climb_restarts', '    return any('),
    observations=[
        ('table', ('Table 4.1', 'Plain hill climbing on eight queens'), ['Run', 'Number of starts', 'Successes', 'Success rate p (%)'], [
            ['Seeds 0–199', str(o4['trials']), str(o4['successes']), f'{100 * o4["successes"] / o4["trials"]:.1f}'],
            ['Seeds 10 000–10 199', str(o4['trials']), str(o4['successes_repeat']), f'{100 * o4["successes_repeat"] / o4["trials"]:.1f}'],
            ['Seeds 0–199, ≤ 100 sideways moves', str(o4['trials']), str(o4['sideways_successes']), f'{100 * o4["sideways_successes"] / o4["trials"]:.1f}']],
         [2.4, 1.2, 1, 1.3]),
        ('table', ('Table 4.2', 'Success rate against number of restarts k'), ['Restarts k', 'Trials', 'Measured success (%)', f'Predicted 1 − (1 − p)^k (%), p = {p4:.3f}'],
         [[str(r['k']), str(r['trials']), f"{r['measured']:.1f}", f"{r['predicted']:.1f}"] for r in o4['restarts']]),
        ('para', f'Restarts needed for 99% success at p = {p4:.3f}: {o4["k99"]}. On the 1-D landscape {o4["n_local_maxima"]} '
                 f'local maxima were found (global maximum at x = {o4["x_global"]:.2f}); only {100 * o4["oned_reach_global"]:.0f}% '
                 f'of 25 evenly spaced starts climbed to the global one.'),
    ],
    results=[
        ('fig', LAB / 'exp04-hillclimb/figs/fig4_1_landscape.png', ('Figure 4.1', 'The objective landscape with local maxima marked'), 14),
        ('fig', LAB / 'exp04-hillclimb/figs/fig4_2_restarts.png', ('Figure 4.2', 'Success rate against number of restarts, measured and predicted'), 12),
        ('para', f'A single climb solved eight queens in {o4["successes"]} of {o4["trials"]} starts (12.5%), and '
                 f'{o4["successes_repeat"]} of {o4["trials"]} (16.0%) with other seeds (Table 4.1). Restarts raised this to '
                 f'{o4["restarts"][-1]["measured"]:.1f}% at k = 20 ({o4["trials"]} trials). The measured curve follows the prediction '
                 'but lies 2–7 points above it (Table 4.2, Figure 4.2). Allowing sideways moves raised a single climb to 94.5%.'),
    ],
    discussion=[
        'I expected a single climb to succeed about one time in six and restarts to follow 1 − (1 − p)^k. The two plain runs gave '
        '12.5% and 16.0%; with 200 trials the binomial standard error is √(p(1 − p)/200) ≈ 2.4 points, so these two values are '
        'consistent with each other and with the manual’s 15.5%.',
        'The measured restart curve lies above the prediction at every k (for example 56.0% against 48.7% at k = 5). The prediction '
        'uses p = 0.125 from the first seed set, which by chance was at the low end; the k = 1 point of the restart run itself is '
        '14.5%. Using p ≈ 0.145 gives 54.3% at k = 5 and 95.6% at k = 20, close to my measurements. So the gap comes from '
        'uncertainty in p, not from correlated restarts. Correlated restarts would push the curve below the prediction.',
        'The sideways-move result (94.5%) was the biggest surprise. Most failures of plain hill climbing on eight queens are not '
        'strict local minima but plateaus, where a queen can move without changing h. Letting the climber walk across them fixes '
        'most failures without any restart.',
    ],
    answers=[
        'It gets stuck at a local maximum (all neighbours worse), on a plateau (all neighbours equal, including shoulders and flat '
        'maxima), and on a ridge (improvement needs a combined move no single step offers). Sideways moves fix shoulders, the '
        'plateaus that lead on to a better state; they cannot fix a true local maximum or a flat maximum. In my runs they raised '
        'success from 12.5% to 94.5%.',
        'Hill climbing keeps only the current board and the best neighbour found so far, a fixed amount of memory whatever the '
        'depth. Backtracking must keep the recursion stack (the partial assignment of up to n columns), and BFS-like systematic '
        'search would keep a whole frontier. Hill climbing never needs to return to an earlier state, so it never stores one.',
        'k = ln(0.01)/ln(1 − 0.155) = 4.605/0.168 ≈ 27.4, so 28 restarts (35 with my p = 0.125). The calculation assumes each '
        'restart is an independent trial with the same success probability p, i.e. that the random starting boards are '
        'independent and that p is known exactly.',
        'For n = 1000 hill climbing (min-conflicts style local repair) is far better. Backtracking’s node count grows about 4.7 times '
        'per extra column in my measurements, which is hopeless at n = 1000. A local search that starts from a full board and '
        'repairs conflicts uses constant memory, and in practice solves even million-queen boards in a number of steps roughly '
        'linear in n.',
        'No. Each figure is an estimate from 200 random trials, with a standard error of about √(0.14·0.86/200) ≈ 2.5 percentage '
        'points. 12.5% and 15.5% differ by about 1.2 standard errors, which is normal sampling variation. I also measured 12.5% and '
        '16.0% on two seed sets. The program would only be suspect if repeated runs differed by much more than this.',
    ],
    conclusion=f'Steepest-ascent hill climbing solved eight queens from only about 1 start in 7 ({100 * p4:.1f}%) because it '
               'stops on plateaus and local minima. Random restarts raised success to about 97% at k = 20, close to the '
               'independent-trials prediction, and sideways moves alone reached 94.5%. Local search with restarts is used for '
               'large scheduling and layout problems, and for escaping local minima of potential fields in robot motion planning.',
)

# --------------------------------------------------------------------------- Experiment 5
o5 = J('exp05-rl/obs.json')
r5 = {r['eps']: r for r in o5['rows']}
comment5 = {0.01: 'Highest return; almost always greedy', 0.1: 'Near-optimal; one seed slower to settle',
            0.2: 'Same policy, a few random steps per episode', 0.5: 'Same greedy policy, but acts randomly half the time'}
E5 = dict(
    n=5, title='Reinforcement Learning (Tabular Q-Learning)', source='Lab Manual, Chapter 6', header_line=header('4'),
    aim='To formulate a navigation task as a Markov decision process, to implement Q-learning on a grid world, and to '
        'measure the effect of the exploration rate on what is learned and how quickly.',
    objectives=[
        'Describe a grid navigation task as states, actions, transitions and rewards.',
        'Implement tabular Q-learning with an ε-greedy behaviour policy and explain each term of the update.',
        'Compare learning curves and final return for four exploration rates.',
        'Extract the greedy policy, draw it, and check it against the optimal policy from value iteration.',
    ],
    software=SW,
    theory=[
        'A Markov decision process has states s, actions a, a transition rule s′ = T(s, a) and a reward r for each transition; '
        'the agent looks for a policy that maximises the expected discounted return Σ γ^t r_t [7]. Q-learning learns the action '
        'value Q(s, a), the return expected after taking a in s and acting optimally afterwards, from experience alone, without a model:',
        'Q(s, a) ← Q(s, a) + α [ r + γ · max_a′ Q(s′, a′) − Q(s, a) ]',
        'The bracket is the temporal-difference (TD) error: the target r + γ max Q(s′, ·) minus the current estimate. The learning '
        'rate α sets how much of that error is absorbed per step, and the discount γ sets how far ahead the agent looks. At a '
        'terminal state there is no future, so the γ·max term is dropped. Q-learning is off-policy: the max learns the value of '
        'the greedy policy even while the agent behaves ε-greedily (random action with probability ε), which is what lets it explore '
        'and still converge to the optimal action values [7].',
        'The grid world is 5 × 7 with five wall cells. The goal (0, 6) gives +10 and ends the episode, the pit (2, 6) gives −10 and '
        'ends it, and every other step costs −0.1. Bumping a wall leaves the agent in place. The step cost and γ < 1 both reward '
        'short routes.',
    ],
    procedure=[
        f'Defined the environment and step(s, a) as above; start (4, 0); episode cap {o5["cap"]} steps.',
        f'Initialised Q = 0 (5 × 7 × 4). For each of {o5["episodes"]} episodes acted ε-greedily, applied the update after every '
        f'step with α = {o5["alpha"]}, γ = {o5["gamma"]}, and recorded the total reward (generator seed {o5["seed"]}).',
        'Repeated for ε = 0.01, 0.10, 0.20 and 0.50, plotted 25-episode moving averages (Figure 5.1), and computed the mean '
        'return over the last 100 episodes. Repeated each ε with seeds 0–4 to measure the spread.',
        'Extracted the greedy policy argmax_a Q(s, a), drew it (Figure 5.2), followed it from the start, and compared its return '
        'with the optimal return from value iteration on the known model.',
        'For question 4, retrained ε = 0.20 with the step cost set to 0.',
    ],
    code_intro='Key part of the program (full notebook: exp05-rl/exp05.ipynb):',
    code=find_lines('exp05-rl/exp05.py', 'def step', '    return ns, step_cost, False') + '\n\n' +
         find_lines('exp05-rl/exp05.py', 'def train', '    return Q, np.array(curve)'),
    observations=[
        ('table', ('Table 5.1', 'Environment and learning parameters'), ['Quantity', 'Value'], [
            ['Grid dimensions', '5 rows × 7 columns, 5 wall cells, start (4, 0)'],
            ['Reward structure (goal / step / trap)', '+10 / −0.1 / −10 (goal and trap end the episode)'],
            ['Learning rate α', str(o5['alpha'])], ['Discount factor γ', str(o5['gamma'])],
            ['Number of episodes', f'{o5["episodes"]} (cap {o5["cap"]} steps per episode)'],
            ['Random seed', f'{o5["seed"]} (spread: seeds 0–4)']], [1.3, 1.7]),
        ('table', ('Table 5.2', 'Mean return over the last 100 episodes'),
         ['Exploration rate ε', 'Mean return (last 100), seed 0', 'Seeds 0–4, mean ± SD', 'Greedy policy optimal?', 'Comment'],
         [[f'{e:.2f}', f"{r5[e]['mean_last100']:.2f}", f"{r5[e]['seeds_mean']:.2f} ± {r5[e]['seeds_sd']:.2f}",
           'Yes' if o5['policy_check'][str(e)]['optimal'] else 'No', comment5[e]] for e in (0.01, 0.1, 0.2, 0.5)],
         [1, 1.2, 1.3, 1.1, 2.4]),
        ('para', 'Extracted greedy policy (ε = 0.20; # wall, G goal, P pit). Following it from the start reaches the goal in '
                 f'{o5["opt_steps"]} steps with return {o5["opt_return"]:.2f}, the optimal return found by value iteration:'),
        ('code', '\n'.join(o5['policy_grid'])),
    ],
    results=[
        ('fig', LAB / 'exp05-rl/figs/fig5_1_learning_curves.png', ('Figure 5.1', 'Learning curves (return per episode, 25-episode moving average) for each ε'), 15),
        ('fig', LAB / 'exp05-rl/figs/fig5_2_policy.png', ('Figure 5.2', 'Extracted greedy policy shown as arrows on the grid (ε = 0.20)'), 11),
        ('para', 'All four agents learned within about 50 episodes (Figure 5.1). The final mean return fell as ε rose, from 9.08 '
                 '(ε = 0.01) to 7.44 (ε = 0.50) (Table 5.2), yet every agent’s greedy policy reaches the goal in 10 steps with '
                 'return 9.10, the optimum from value iteration. Figure 5.2 shows the route: up the left side, along the top row, '
                 'and never past the pit.'),
    ],
    discussion=[
        'I expected small ε to learn more slowly and large ε to earn less. The second part held clearly: ε = 0.50 averaged 7.44 '
        'over the last 100 episodes against 9.08 for ε = 0.01. The first part barely showed. Even ε = 0.01 found the goal by '
        'episode 3, because Q starts at 0 while every step costs −0.1, so actions already tried look worse than untried ones. '
        'This "optimism" explores systematically even with almost no random actions.',
        'The drop at high ε is behaviour, not learning: all four greedy policies are optimal (10 steps, return 9.10). The ε = 0.50 '
        'agent knows the best route but takes a random action half the time. It earns less while learning, which is why ε is '
        'usually decayed during training. The ε = 0.10 result had the largest spread across seeds (8.79 ± 0.30), so one seed (my '
        'seed 0, 9.00) is not enough to rank 0.10 against 0.20.',
        'Removing the step cost did not change the route here (still 10 steps). With γ = 0.95 a reward reached later is already '
        'worth less, so discounting alone favours the shortest path in this small grid. The step cost matters more when γ is close to 1.',
    ],
    answers=[
        'Q(s, a) is the current estimate, α the learning rate (fraction of the error absorbed), r the reward just received, γ the '
        'discount (weight of the future), and max_a′ Q(s′, a′) the estimated value of acting optimally from the next state. The '
        'bracket r + γ max Q(s′, ·) − Q(s, a) is the temporal-difference error: what was observed (one real step plus the estimate '
        'from there) minus what was predicted.',
        'A terminal state has no next state and no further reward. If γ·max Q(s′, ·) were kept, the agent would add the value of '
        'states "after the end" (the goal or pit cell’s own Q, which is never updated meaningfully). The values become wrong and can '
        'grow without bound. Multiplying by (not done) makes the target just r at the goal (+10) and the pit (−10).',
        'No. Its greedy policy is the same optimal 10-step route as the others (return 9.10, Table 5.2). Its lower average return '
        '(7.44) comes from behaviour: half of its actions are random, so it wanders and sometimes falls in the pit, even though '
        'its Q-table already ranks the actions correctly. The learned policy and the exhibited behaviour are different things.',
        'It makes every extra step cost something, so shorter routes to the goal score higher and the agent prefers them. It also '
        'makes untried actions look better than tried ones early on, which helps exploration. Without it, all paths that '
        'eventually reach the goal would score the same when γ = 1. In my run with γ = 0.95 the route stayed 10 steps, because '
        'discounting already penalises delay.',
        'Off-policy means it learns the value of one policy (the greedy, optimal one, via the max) while following another (the '
        'ε-greedy behaviour policy). The update target does not depend on which action is actually taken next, so the agent can '
        'take random exploratory actions and still learn the optimal Q-values. SARSA, which is on-policy, would learn the value of '
        'the exploring policy instead.',
    ],
    conclusion='Tabular Q-learning learned the optimal 10-step route around the walls and the pit for every exploration rate tested. '
               'A larger ε lowered the return earned while learning (9.08 at 0.01 to 7.44 at 0.50) without changing the learned '
               'policy, which shows the difference between policy and behaviour. The same algorithm, with a neural network in place '
               'of the table, is used for robot locomotion, manipulation and traffic-signal control.',
)

# --------------------------------------------------------------------------- Experiment 6
o6 = J('exp06-neural/obs.json')
E6 = dict(
    n=6, title='A Simple Neural Network', source='Lab Manual, Chapter 7', header_line=header('5'),
    aim='To implement a two-layer neural network in NumPy alone, to train it on the XOR problem by backpropagation, and to '
        'observe the effect of the learning rate on convergence.',
    objectives=[
        'Show, by training one, that a single sigmoid unit cannot represent XOR.',
        'Implement the forward pass, squared-error loss, backpropagation and gradient descent for a 2-4-1 network without a framework.',
        'Train to convergence and check the four outputs.',
        'Measure how the learning rate changes convergence, and draw the learned decision surface.',
        'Show what zero initialisation does to the hidden units.',
    ],
    software=SW + ' No machine-learning framework is used.',
    theory=[
        'A single unit computes y = σ(wᵀx + b) and its decision boundary y = 0.5 is the straight line wᵀx + b = 0. XOR '
        'needs (0,0) and (1,1) on one side and (0,1) and (1,0) on the other, which no straight line can do, so XOR is not '
        'linearly separable. A hidden layer maps the inputs to new features h in which the classes are separable [8].',
        'With the sigmoid σ(z) = 1/(1 + e^(−z)) the network computes h = σ(XW₁ + b₁) and o = σ(hW₂ + b₂), and is trained to '
        'minimise E = mean (o − y)². The chain rule, together with σ′(z) = σ(z)(1 − σ(z)), gives the deltas from quantities '
        'already computed in the forward pass:',
        'δ_o = (o − y) · o(1 − o),   δ_h = (δ_o W₂ᵀ) · h(1 − h),   ∇W₂ = hᵀδ_o,   ∇W₁ = Xᵀδ_h,   ∇b = Σ δ',
        'Gradient descent then updates every parameter by −η × gradient, where η is the learning rate. Weights must start random: '
        'if every hidden unit starts identical, every unit receives the same gradient and they stay identical forever [8].',
    ],
    procedure=[
        'Wrote the four XOR pairs as arrays X (4 × 2) and y (4 × 1).',
        'Trained a single sigmoid unit (no hidden layer) for 20 000 epochs as a baseline.',
        f'Initialised W₁ (2 × 4) and W₂ (4 × 1) from N(0, 1) with seed {o6["seed"]}, biases at zero, and trained the 2-4-1 network '
        f'for {o6["epochs"]} epochs of full-batch gradient descent, recording the MSE every epoch.',
        'Repeated for learning rates 0.05, 0.5, 2.0 and 10.0 and plotted the loss curves on a log axis (Figure 6.1).',
        'Took the run with the lowest final loss, printed its four outputs and plotted its output over a 300 × 300 grid of the '
        'input plane with the 0.5 contour (Figure 6.2).',
        'Trained once more with all weights initialised to zero.',
    ],
    code_intro='Key part of the program (full notebook: exp06-neural/exp06.ipynb):',
    code=find_lines('exp06-neural/exp06.py', 'def train_xor', '    return (W1, b1, W2, b2), loss'),
    observations=[
        ('table', ('Table 6.1', 'Network and training set-up'), ['Quantity', 'Value'], [
            ['Network shape (input-hidden-output)', '2-4-1'], ['Activation functions', 'Sigmoid in hidden and output layers'],
            ['Loss', 'Mean squared error over the 4 XOR patterns'], ['Initialisation seed', f'{o6["seed"]} (weights N(0, 1), biases 0)'],
            ['Epochs', f'{o6["epochs"]:,} (full batch)'.replace(',', ' ')], ['Learning rates tried', '0.05, 0.5, 2.0, 10.0']], [1.4, 1.6]),
        ('table', ('Table 6.2', 'Effect of learning rate'), ['Learning rate', 'Final MSE', 'First epoch with MSE < 0.01', 'Converged? (Yes / No)'],
         [[str(r['lr']), f"{r['final_mse']:.2e}", str(r['epoch_mse_below_1e2']), 'Yes' if r['converged'] else 'No (still descending)']
          for r in o6['rows']]),
        ('table', ('Table 6.3', f'Predicted outputs after training (best run, learning rate {o6["best_lr"]})'), ['x1', 'x2', 'Target', 'Predicted (3 d.p.)'],
         [[a, b, t_, f'{p:.3f}'] for (a, b, t_), p in zip([('0', '0', '0'), ('0', '1', '1'), ('1', '0', '1'), ('1', '1', '0')], o6['best_pred'])]),
        ('para', 'Converged means all four outputs are on the correct side of 0.5 and the final MSE is below 10⁻³. Single sigmoid '
                 f'unit (no hidden layer): outputs {o6["single_unit"]["outputs"]}, MSE {o6["single_unit"]["mse"]:.3f}. Zero-initialised '
                 f'2-4-1 network (η = 2.0): outputs {o6["zero_init"]["outputs"]}, MSE {o6["zero_init"]["mse"]:.3f}, all four hidden '
                 'units with identical weights at the end.'),
    ],
    results=[
        ('fig', LAB / 'exp06-neural/figs/fig6_1_loss.png', ('Figure 6.1', 'Loss curve for each learning rate (log scale)'), 15),
        ('fig', LAB / 'exp06-neural/figs/fig6_2_decision_boundary.png', ('Figure 6.2', 'Decision boundary of the trained network over the input plane'), 10),
        ('para', 'With η = 0.05 the loss stayed on a plateau near 0.25 for about 7000 epochs and had not converged after 20 000 '
                 '(MSE 2.3 × 10⁻³). The three larger rates converged, faster as η increased: MSE fell below 0.01 at epoch 1086, 272 '
                 'and 70 respectively (Table 6.2, Figure 6.1). The best run outputs 0.002, 0.998, 0.998 and 0.003 (Table 6.3), and its '
                 '0.5 contour is two parallel lines that put the two 1-cases in a band between them (Figure 6.2).'),
    ],
    discussion=[
        'I expected larger learning rates to converge faster up to a point, and the largest one (10.0) to oscillate or diverge, '
        'as the manual suggests. Up to 2.0 my results match the manual’s numbers (2.31 × 10⁻³, 1.11 × 10⁻⁴, 2.46 × 10⁻⁵), as they '
        'should with the same seed. η = 10 was not unstable: it converged fastest of all (MSE < 0.01 at epoch 70, final 5.8 × 10⁻⁶). '
        'The reason is that the sigmoid limits every activation to (0, 1), so the gradients o(1 − o) and h(1 − h) are at most 0.25, '
        'and with only four training points the loss surface is smooth. A rate this large would almost certainly diverge on a '
        'bigger network or with unbounded activations such as ReLU.',
        'The long flat start of every curve is the network sitting near its symmetric starting point, where all outputs are about '
        '0.5 and the gradient is tiny. Once the hidden units specialise into different features in which XOR is separable, the loss '
        'drops by orders of magnitude.',
        'The two control runs support the theory directly. A single unit ended with all four outputs at 0.5 (MSE 0.25), the best a '
        'straight-line boundary can do on XOR. The zero-initialised network did exactly the same, and its hidden units kept identical '
        'weights after 20 000 epochs, so it behaved as a single unit.',
    ],
    answers=[
        'A single unit’s boundary is a straight line wᵀx + b = 0, and no line separates {(0,0), (1,1)} from {(0,1), (1,0)}. My single '
        'unit stalled at output 0.5 for every input. The hidden layer computes new features of the inputs (for example, OR-like and AND-like units) '
        'in which XOR is linearly separable, so the output unit can draw its line in that space. In the input plane this appears as '
        'the curved band of Figure 6.2.',
        'With all weights zero every hidden unit computes the same value and receives the same gradient, because δ_h depends on W₂, '
        'which is also identical for every unit. The units stay identical forever, so the network has the power of one hidden unit '
        'and cannot learn XOR. My zero-initialised run stayed at MSE 0.25 with identical columns in W₁.',
        'It is the derivative of the output sigmoid. With E = (o − y)² (up to a constant factor) and o = σ(z), the chain rule gives '
        '∂E/∂z = (o − y)·σ′(z), and σ′(z) = σ(z)(1 − σ(z)) = o(1 − o). It can be computed from the output already known from the '
        'forward pass, without evaluating any exponential again.',
        'The network is stuck near a saddle point or plateau of the loss. Starting from small random weights, all outputs are close '
        'to 0.5 and the hidden units are nearly interchangeable, so the gradient is very small. Slowly the symmetry breaks: the units '
        'specialise into useful features, the gradient grows, and the loss falls sharply. This was clearest for η = 0.05, flat '
        'until about 7000 epochs.',
        'Experiment 4, hill climbing: gradient descent is hill climbing (descending) on a continuous, differentiable landscape, taking '
        'the steepest direction at every step. They share the failure of getting stuck where there is no local improvement: local '
        'minima, plateaus and saddle points. The usual remedies are also similar: random restarts or random initialisation, momentum, and noise.',
    ],
    conclusion='A 2-4-1 sigmoid network written in NumPy learned XOR, which a single unit cannot, reaching outputs within 0.003 of '
               'the targets. Learning rates from 0.5 to 10 converged, faster for larger η on this tiny problem; 0.05 had not converged '
               'after 20 000 epochs, and zero initialisation never broke symmetry. The same forward-backward-update loop trains '
               'the perception, inverse-kinematics and value networks used on modern robots.',
)

# --------------------------------------------------------------------------- Experiment 8
def rows_csv(path):
    with open(LAB / path) as f:
        return list(csv.DictReader(f))
pct = lambda v: f'{100 * float(v):.0f}%'
R8 = 'exp08-xembody/results/'
emb = rows_csv(R8 + '01_embodiments.csv')
js = rows_csv(R8 + '02_joint_space_transfer.csv')
ts = rows_csv(R8 + '03_task_space_transfer.csv')
l4 = rows_csv(R8 + '04_learn_once_deploy_many_kuka_iiwa.csv')
l4x = rows_csv(R8 + '04_learn_once_deploy_many_xarm6.csv')
m5 = rows_csv(R8 + '05_multi_embodiment.csv')
e4s = rows_csv(R8 + 'e4_scale_sweep.csv')
ROB = ['kuka_iiwa', 'franka_panda', 'xarm6', 'kuka_mini']
def sr(rows, robot, policy):
    return pct(next(r['success_rate'] for r in rows if r['robot'] == robot and r['policy'] == policy))
def m5v(held, training, obs):
    r = next(r for r in m5 if r['held_out'] == held and r['training'] == training and r['obs'] == obs)
    return pct(r['success_rate']) + (f" ({r['trained_on'].replace('_', ' ').replace('+', ' + ')})" if obs == 'agnostic' else '')
E8 = dict(
    n=8, title='Cross-Embodiment Transfer of a Manipulation Skill (PyBullet)',
    source='Zip: AISR-Cross-Embodiment-PyBullet (README.md, MANUAL.md, docs/MANUAL.pdf)',
    header_line=f'Date performed: {RUN_DATE}     Session: –     Partner: {PARTNER}',
    aim='To study whether a pick-and-place skill developed on one robot arm can be transferred to robot arms with different '
        'kinematics, numbers of joints and sizes, and to identify which design choices make the transfer succeed or fail.',
    objectives=[
        'Describe four arms by measurable embodiment quantities: degrees of freedom, reach and task coverage.',
        'Show that replaying one robot’s joint angles on another robot does not transfer a skill.',
        'Transfer the skill through a shared task-space action interface with a per-robot inverse-kinematics adapter.',
        'Train behaviour-cloning policies on one robot and test them zero-shot on robots never seen in training, comparing a '
        'body-independent observation with one that includes joint angles.',
        'Separate interface problems (fixable in software) from capability problems (the body cannot do the task).',
    ],
    software='Python 3.11.16, PyBullet 3.2.7 (built from source with CFLAGS="-Dfdopen=fdopen" for the macOS 27 SDK), '
             'NumPy 2.4.6, scikit-learn 1.9.1, Matplotlib; macOS 27, Apple M5. Simulated robots: KUKA LBR iiwa (7-DOF), Franka '
             'Emika Panda (7-DOF), UFactory xArm6 (6-DOF) and the KUKA iiwa scaled to 70% (kuka_mini), each with a suction-cup '
             'gripper abstraction; 5 cm cube and a goal disc on the floor; 30 Hz control, 300-step episodes [13], [14].',
    theory=[
        'A robot’s embodiment is everything about its body that decides how a command becomes motion: the number of joints, '
        'link lengths, joint limits, actuator strength, gripper and mounting. Forward kinematics x = FK(q) maps joint angles q to '
        'the tool pose x, and inverse kinematics q = IK(x) solves the reverse problem. Both are different functions for every '
        'robot, so the same q gives different tool poses on different arms, while the same desired x can be sent to any arm that '
        'has its own IK [14]. For a 7-DOF arm IK has infinitely many solutions, and PyBullet’s damped-least-squares solver picks one '
        'using null-space rest poses.',
        'The embodiment gap has four parts: the action-space gap (different joints), the observation gap (inputs that mean different '
        'things on each body), the dynamics gap (torques, masses, speeds) and the capability gap (the body cannot reach or do the '
        'task). The first two can be closed in software by expressing actions as tool displacements (dx, dy, dz, grip) and '
        'observations as tool, cube and goal positions in the robot’s own base frame; the last cannot [14], [15].',
        'Behaviour cloning (BC) trains a network by supervised learning on (observation, expert action) pairs, here a 2 × 256 ReLU MLP. '
        'Its weakness is covariate shift: small mistakes lead to states the expert never visited, and errors compound [17]. DART '
        'injects noise into the executed action while keeping the clean expert action as the label, so the data shows how to '
        'recover from mistakes [16]. Training on several bodies (multi-embodiment training, as in RT-X and Octo) aims to make a '
        'policy rely on what the bodies share [15].',
    ],
    procedure=[
        'Built a Python 3.11 environment and ran experiments/00_check_setup.py (ended with SETUP OK).',
        'Ran python run_all.py, which runs Parts 1–5 headless with the default sizes: 3000 random joint samples (Part 1), 10 '
        'joint-space replays (Part 2), 20 task-space episodes per robot (Part 3), 60 noisy-expert demonstrations and 20 test '
        'layouts (Part 4), and leave-one-embodiment-out with a 60-demonstration budget (Part 5). It also saves a side-by-side GIF.',
        'Exercise E1: python experiments/04_learn_once_deploy_many.py --source xarm6 (BC trained only on the xArm6).',
        'Exercise E4: wrote experiments/e4_scale_sweep.py, which sets the KUKA’s global scale to 0.6–1.0 and runs the task-space '
        'expert on the 20 Part 3 layouts at each scale (python experiments/e4_scale_sweep.py --episodes 20).',
        'Copied every CSV, figure, log and my script into exp08-xembody/ of the repository. All random seeds are fixed by the project.',
    ],
    code_intro='Key part of the code: my exercise E4 script (exp08-xembody/exercises/e4_scale_sweep.py). The policy, task and '
               'seeds stay fixed and only the robot’s scale changes:',
    code=find_lines('exp08-xembody/exercises/e4_scale_sweep.py', '    policy = lambda', "        print(f\"  scale {s:.2f}"),
    observations=[
        ('table', ('Table 8.1', 'Embodiments (Part 1)'), ['Robot', 'Arm DOF', 'Max reach (m)', 'Task coverage (%)'],
         [[r['robot'], r['dof'], f"{float(r['max_reach_m']):.2f}", f"{100 * float(r['task_coverage']):.0f}"] for r in emb]),
        ('table', ('Table 8.2', 'Joint-space replay of KUKA trajectories (Part 2, 10 episodes)'),
         ['Robot', 'Success rate', 'Mean path deviation (cm)', 'Median cube-goal error (cm)'],
         [[r['robot'] + (' (itself)' if r['robot'] == 'kuka_iiwa' else ''), pct(r['success_rate']),
           f"{float(r['path_dev_mean_cm']):.1f}", f"{float(r['cube_goal_err_cm']):.2f}"] for r in js]),
        ('table', ('Table 8.3', 'Task-space transfer of the expert (Part 3, 20 episodes)'),
         ['Robot', 'Success rate', 'Mean steps (successful)', 'Median cube-goal error (cm)'],
         [[r['robot'], pct(r['success_rate']), f"{float(r['mean_steps']):.1f}", f"{float(r['median_error_cm']):.2f}"] for r in ts]),
        ('table', ('Table 8.4', 'Learn on KUKA, deploy everywhere (Part 4, success rates, 20 episodes)'),
         ['Robot', 'Expert', 'BC-agnostic', 'BC-proprio'],
         [[rb + (' (source)' if rb == 'kuka_iiwa' else ''), sr(l4, rb, 'expert'), sr(l4, rb, 'BC-agnostic'), sr(l4, rb, 'BC-proprio')] for rb in ROB]),
        ('table', ('Table 8.5', 'Leave-one-embodiment-out (Part 5, success on the unseen robot, 20 episodes)'),
         ['Unseen robot', 'single, agnostic', 'multi, agnostic', 'single, proprio', 'multi, proprio'],
         [[h, m5v(h, 'single', 'agnostic'), m5v(h, 'multi', 'agnostic'), m5v(h, 'single', 'proprio'), m5v(h, 'multi', 'proprio')]
          for h in ['kuka_iiwa', 'franka_panda', 'xarm6']], [1.1, 1.4, 1.6, 1, 1]),
        ('table', ('Table 8.6', 'Exercises E1 and E4 (20 episodes per entry)'), ['Exercise', 'Change made', 'Measured effect'], [
            ['E1', 'BC trained only on xarm6 (60 demos)',
             f"Expert / BC-agnostic / BC-proprio: kuka_iiwa {sr(l4x, 'kuka_iiwa', 'expert')} / {sr(l4x, 'kuka_iiwa', 'BC-agnostic')} / {sr(l4x, 'kuka_iiwa', 'BC-proprio')}; "
             f"franka_panda {sr(l4x, 'franka_panda', 'expert')} / {sr(l4x, 'franka_panda', 'BC-agnostic')} / {sr(l4x, 'franka_panda', 'BC-proprio')}; "
             f"xarm6 (source) {sr(l4x, 'xarm6', 'expert')} / {sr(l4x, 'xarm6', 'BC-agnostic')} / {sr(l4x, 'xarm6', 'BC-proprio')}; "
             f"kuka_mini {sr(l4x, 'kuka_mini', 'expert')} / {sr(l4x, 'kuka_mini', 'BC-agnostic')} / {sr(l4x, 'kuka_mini', 'BC-proprio')}"],
            ['E4', 'KUKA global scale 0.6–1.0, task-space expert',
             'Success: ' + ', '.join(f"{float(r['scale']):.2f} → {pct(r['success_rate'])}" for r in e4s)]],
         [0.6, 1.6, 3.4]),
    ],
    results=[
        ('fig', LAB / 'exp08-xembody/figs/01_workspace.png', ('Figure 8.1', 'Workspace of the four arms (green box: task area)'), 15.5),
        ('fig', LAB / 'exp08-xembody/figs/02_joint_space_paths.png', ('Figure 8.2', 'Joint-space replay paths (black dashed: KUKA source path)'), 15.5),
        ('fig', LAB / 'exp08-xembody/figs/03_task_space_paths.png', ('Figure 8.3', 'Task-space transfer paths for the same layout'), 15.5),
        ('fig', LAB / 'exp08-xembody/figs/04_learn_once_deploy_many_kuka_iiwa.png', ('Figure 8.4', 'Learn once on the KUKA, deploy on every robot (Part 4)'), 14.5),
        ('fig', LAB / 'exp08-xembody/figs/05_multi_embodiment.png', ('Figure 8.5', 'Multi-embodiment training result (Part 5)'), 14.5),
        ('fig', LAB / 'exp08-xembody/figs/e4_scale_sweep.png', ('Figure 8.6', 'Exercise E4: task success against KUKA scale'), 11.5),
        ('para', 'Copying joint angles worked only on the KUKA itself (100%); every other body failed (0%), with tool paths 17–27 cm '
                 'off (Table 8.2, Figure 8.2). Sending the same task-space commands through each robot’s IK gave 100% on the KUKA, '
                 'Panda and xArm6, but 30% on the 70% KUKA (Table 8.3, Figure 8.3). A BC policy trained only on the KUKA transferred '
                 'zero-shot to the Panda and xArm6 (100%) when it saw task-space features only, and failed everywhere except the '
                 'source (0%) when it also saw joint angles (Table 8.4, Figure 8.4). Training on two bodies did not rescue BC-proprio '
                 '(0–5%) (Table 8.5, Figure 8.5). Success rose from 0% at scale 0.6 to 100% from scale 0.85 (Figure 8.6).'),
    ],
    discussion=[
        'I expected joint-space replay to fail on other bodies, task-space transfer to succeed when the body can reach, and the '
        'joint-aware policy to transfer worse. All three held, and the proprio result was more extreme than I expected: 0% on every '
        'other robot, not merely worse. My numbers match the instructor’s reference run in MANUAL.md Appendix A exactly. That is '
        'expected, because every seed in the project is fixed and the library versions are almost the same; the manual says the '
        'same seeds give the same numbers.',
        'Analysis questions (MANUAL.md Section 8):',
        ('numbered', [
            'Same joints and angles, but every link is 70% as long, so FK maps the same q to a shrunken copy of the path (Figure 8.2), '
            'which never reaches the cube. A skill stored as joint angles is tied to link lengths, not just joint structure.',
            'The links, offsets and joint axes differ, so the same seven angles produce a different tool pose. Panda’s joint 4 bends '
            'only one way, so some KUKA angles are clipped. Path deviation was 16.7 cm with 0% success.',
            'kuka_mini still fails (30%). The cause is the body: Table 8.1 shows reach 0.66 m and only 48% task coverage with the tool '
            'pointing down, while the interface works for the other three bodies.',
            'BC-proprio uses the KUKA’s joint angles as inputs, and on another robot those numbers mean different things (Panda/xArm6 '
            'angles for the same tool pose are different, and xArm6 has a zero-padded 7th joint). The policy sees inputs outside its '
            'training distribution: an observation gap. BC-agnostic sees only quantities that mean the same on every body.',
            'Both use the same task-space interface, so both are limited by which layouts the short arm can reach (expert 50%, '
            'BC-agnostic 55% on the 20 test layouts). They can differ by an episode because BC’s actions are slightly different from '
            'the expert’s, which changes how close the arm gets to marginal, near-edge goals.',
            'No. Multi-embodiment training gave BC-proprio 0–5% on the unseen robot, the same as single-robot training. Two bodies are '
            'not enough to make the joint inputs meaningless to the network. For BC-agnostic it did not matter (100% either way) because '
            'its inputs are already body-independent.',
            'A real gripper adds grasp pose and finger geometry: the approach orientation and finger width must match the object. It '
            'also adds contact dynamics (friction, slip, force limits), which differ between grippers and are not captured by a '
            'tool-position action.',
            'Bring the task within reach: mount kuka_mini closer to the task area or on a pedestal (GUIDE exercise E5), or relax the '
            'tool-down orientation constraint. E4 also shows that a scale of 0.85 or more is already enough.',
        ]),
        'Exercises: in E1 (source xArm6) the pattern repeated: BC-agnostic transferred (100% KUKA, 95% Panda) and BC-proprio was 0% '
        'off the source, so the result does not depend on which robot is the source. E4 located the capability limit: success rises '
        'steeply from 0.70 (30%) to 0.80 (95%), and from 0.85 the scaled KUKA is as good as the full-size one.',
        'Result (MANUAL.md Section 10): joint-space transfer succeeded only on the source robot (0% elsewhere), while task-space '
        'transfer succeeded on every full-size arm (100%) and on 30% of layouts for the 70% KUKA. Zero-shot, BC-agnostic reached '
        '100% on the Panda and xArm6 and BC-proprio 0%. The joint-space and BC-proprio failures were interface and observation '
        'problems, fixed by design; the kuka_mini failures were capability limits of the body itself.',
    ],
    answers=[
        'It is the set of differences between two robot bodies that stop a skill transferring directly. Action gap: KUKA has 7 joints, '
        'xArm6 has 6. Observation gap: joint angles mean different poses on the Panda and KUKA. Dynamics gap: different motor torques, '
        'speeds and masses. Capability gap: the 70% KUKA cannot reach half the task area (48% coverage).',
        'Every arm’s job is to move its tool through the same 3-D workspace, and positions and displacements in that space mean the '
        'same thing for every body. Each robot then turns a tool command into its own joint motion with its own IK, so a single policy '
        'can speak to all of them. That is why task-space transfer reached 100% on three different arms.',
        'A 7-DOF arm has one redundant degree of freedom, so infinitely many joint configurations reach the same tool pose. The rest '
        'pose is a preferred configuration that the solver is pulled towards in the null space. It picks a consistent, comfortable '
        'solution away from joint limits, which prevents the arm from drifting or flipping elbow between steps.',
        'BC is trained only on states the expert visits. At test time small errors push the robot into unfamiliar states where the '
        'policy is worse, so errors compound (covariate shift). DART adds noise to the executed action during demonstration but keeps '
        'the clean expert action as the label, so the data contains slightly-off states together with the correct recovery.',
        'End-effector deltas mean the same thing on every robot, so data from many bodies can be pooled and learned jointly. Joint '
        'angles depend on each robot’s kinematics and joint count, so mixing them across robots would teach contradictory mappings, '
        'as BC-proprio showed with 0% transfer.',
        'When the policy will run on the same body it was trained on and the joint state matters for the task: avoiding joint limits '
        'and self-collision, whole-arm contact, using redundancy (e.g. elbow placement), or dynamic tasks where joint velocities and '
        'torques matter. On the source KUKA, BC-proprio worked perfectly (100%).',
        'Before deployment, sample the task workspace (start, grasp and goal poses at the required tool orientation) and check each '
        'with the new robot’s IK, joint limits and collision model, as Part 1’s task-coverage test does. If coverage is below 100%, flag '
        'the unreachable region or reject the robot. A short scripted-expert rollout on the new body is a second check.',
        'The suction-cup abstraction attaches the cube whenever the tool is within 3 cm of its top face and grip > 0. This hides how '
        'different grippers grasp, so only arm kinematics differ between robots. The experiment isolates the arm-level embodiment '
        'gap, but real two-finger grasping would add its own transfer problems.',
    ],
    conclusion='A skill stored as joint angles did not transfer, even between arms with the same number of joints. Expressing '
               'actions and observations in a shared task space, with each robot’s own IK, let one expert and one learned policy run '
               'unchanged on the Panda and xArm6 (100%). Adding joint angles to the observation tied the policy to its source body '
               '(0% elsewhere), and no interface fixed the short arm’s reach (30%). This is the design used by cross-embodiment robot '
               'datasets and models such as Open X-Embodiment and Octo.',
)

# --------------------------------------------------------------------------- Experiment 7
S7P = LAB / 'exp07-webots/runs/summary.json'
s7 = json.loads(S7P.read_text()) if S7P.exists() else {'runs': [], 'summary': {}}
runs7 = s7['runs']
def agg7(world, setting, key):
    v = s7['summary'].get(f'{world}:{setting}', {}).get(key)
    return v  # (mean, sd, n) or None
def ms(world, setting, key, fmt='{:.1f}'):
    v = agg7(world, setting, key)
    return '–' if v is None else (fmt.format(v[0]) + (' ± ' + fmt.format(v[1]) if v[2] > 1 else ''))
def nrep(world, setting):
    v = agg7(world, setting, 'coverage'); return 0 if v is None else v[2]
swarm_rows = []
for setting, label in (('default', 'default (cruise 0.5)'), ('cruise-0.9', 'cruise = 0.9')):
    rr = sorted([r for r in runs7 if r['world'] == 'swarm' and r['setting'] == setting], key=lambda r: r['run'])
    for r in rr:
        swarm_rows.append([label, str(r['run']), f"{r['path_mean']:.2f}", f"{r['speed_mean']:.3f}",
                           f"{r['stuck_mean']:.1f} (worst {r['stuck_worst']:.1f})", f"{r['coverage']:.0f}"])
    if rr:
        swarm_rows.append([f'{label}: mean ± SD (n = {len(rr)})', '–', ms('swarm', setting, 'path_mean', '{:.2f}'),
                           ms('swarm', setting, 'speed_mean', '{:.3f}'), ms('swarm', setting, 'stuck_mean') + ' (worst ' +
                           ms('swarm', setting, 'stuck_worst') + ')', ms('swarm', setting, 'coverage', '{:.0f}')])
behav = {'default': 'Kept moving (never stuck), but drove the same closed loop for the whole run',
         'bubble-0.15': 'Bubble smaller than half-width: drove into an obstacle and stayed wedged',
         'bubble-0.9': 'Wider berth around obstacles',
         'noise-0.001': 'Lidar noise ≈ 8 cm per beam', 'noise-0.003': 'Lidar noise ≈ 24 cm per beam'}
pio_rows = []
for setting in ('default', 'bubble-0.15', 'bubble-0.9'):
    if nrep('pioneer', setting):
        pio_rows.append([setting.replace('-', ' = '), f"{nrep('pioneer', setting)}", ms('pioneer', setting, 'path_mean', '{:.1f}'),
                         ms('pioneer', setting, 'stuck_worst'), ms('pioneer', setting, 'coverage', '{:.0f}'), behav[setting]])
ex_rows = []
cr = [c for c in ('0.2', '0.4', '0.6', '0.8', '1.0') if nrep('swarm', f'cruise-{c}')]
if cr:
    ex_rows.append(['1. Speed vs safety', 'Swarm cruise = ' + ', '.join(cr) + ' (plus 0.5 and 0.9 from Part A), 120 s, '
                    + ', '.join(f"n = {nrep('swarm', f'cruise-{c}')}" for c in cr),
                    '; '.join(f"cruise {c}: coverage {ms('swarm', f'cruise-{c}', 'coverage', '{:.0f}')}%, worst stuck "
                              f"{ms('swarm', f'cruise-{c}', 'stuck_worst')}%" for c in cr)])
nz = [n for n in ('0.001', '0.003') if nrep('pioneer', f'noise-{n}')]
if nz:
    ex_rows.append(['5. Noisy lidar', 'SICK LMS 291 noise = ' + ', '.join(nz) + ' (≈ 8 and 24 cm), 180 s',
                    '; '.join(f"noise {n}: coverage {ms('pioneer', f'noise-{n}', 'coverage', '{:.0f}')}%, stuck "
                              f"{ms('pioneer', f'noise-{n}', 'stuck_worst')}%, path {ms('pioneer', f'noise-{n}', 'path_mean', '{:.1f}')} m"
                              for n in nz)])
if not nz:
    ex_rows.append(['5. Noisy lidar', 'SICK LMS 291 noise = 0.001 and 0.003 (≈ 8 and 24 cm), added with --lidar-noise',
                    'Attempted but not completed: every headless Pioneer run with noise hung at start-up on this Webots '
                    'nightly build before the deadline, so no measurement is reported.'])
FIG7 = LAB / 'exp07-webots/figs'
shot = sorted(FIG7.glob('fig7_1_screenshot*'))
E7 = dict(
    n=7, title='Mobile Robot Simulation in Webots: Reactive Swarm and Lidar Navigation',
    source='GitHub: github.com/reshamrajs/webots-robotics-sim (README.md and GUIDE.md)',
    header_line=f'Date performed: {RUN_DATE}     Session: –     Partner: {PARTNER}',
    aim='To simulate a swarm of e-puck robots using Braitenberg obstacle avoidance and a Pioneer 3-DX robot using lidar '
        'follow-the-gap navigation, and to measure how controller parameters change coverage, speed and the time a robot spends stuck.',
    objectives=[
        'Run a five-robot e-puck swarm with a Braitenberg controller and measure path length, speed, stuck time and coverage.',
        'Run a Pioneer 3-DX with a SICK LMS 291 lidar and follow-the-gap navigation in an 8 m × 8 m cluttered room.',
        'Change one controller parameter at a time, repeat runs, and report mean and spread.',
        'Explain the speed–safety trade-off and the limits of purely reactive control.',
    ],
    software='Webots R2025a (nightly build of 24 Nov 2026, which fixes the macOS 27 port-detection bug in the R2025a release, '
             'cyberbotics/webots issue 6976), Python 3.15 controllers, Python 3.12 with NumPy and Matplotlib for analysis; macOS 27, '
             'Apple M5. Worlds: worlds/swarm_arena.wbt (5 × e-puck with 8 IR proximity sensors, 1.6 m × 1.6 m arena with boxes and '
             'barrels, supervisor logger) and worlds/pioneer_lidar.wbt (Pioneer 3-DX with SICK LMS 291, 8 m × 8 m room) [9], [10].',
    theory=[
        'A Braitenberg vehicle connects each sensor directly to the wheel speeds with fixed weights, with no map, plan or memory [11]. '
        'The e-puck’s eight IR readings are scaled to x_i ∈ [0, 1] and each wheel gets v = cruise + gain·Σ w_i x_i, clipped to [−1, 1] '
        'and multiplied by the 6.28 rad/s wheel limit and the speed factor. The weights are mirrored, so an obstacle on the right '
        'slows the left wheel and speeds the right one, and the robot turns away. This is reactive control: behaviour comes only '
        'from the current sensor reading [10].',
        'Follow-the-gap takes a 180° lidar scan of 180 beams, clips ranges at lookahead, and marks beams longer than free as open. '
        'It then blanks a safety bubble of angular half-width arctan(bubble/r_min) around the nearest return, finds the widest run of '
        'free beams, and steers to its middle (θ). Forward speed is v = min(max_v, slow·d_front), or 0 when d_front < stop, and the '
        'turn rate is ω = clip(k_turn·θ, ±max_w) [12]. Differential-drive kinematics convert these to wheel speeds: '
        'ω_L = (v − ωL/2)/R and ω_R = (v + ωL/2)/R with R = 0.0975 m and L = 0.33 m [10].',
        'A supervisor robot logs the true position of every robot every 0.32 s. Path length is the summed distance between '
        'samples, stuck % is the share of intervals moving slower than 1 cm/s, and coverage is the share of floor cells (10 cm for '
        'the swarm, 50 cm for the Pioneer) visited by any robot [10].',
    ],
    procedure=[
        'Installed Webots R2025a. On macOS 27 the release build exits at start-up ("failed to open TCP server in the port range '
        '[1234-1244]"), a known bug fixed upstream, so I installed the official nightly R2025a build.',
        'Opened worlds/swarm_arena.wbt in the Webots window, let it run for 120 s, and took the screenshot in Figure 7.1; the logger '
        'wrote analysis/trajectories.csv (Figure 7.2).',
        'Ran experiments headless with tools/run_experiment.py, e.g. python3 tools/run_experiment.py swarm --seconds 120 --set cruise=0.9 '
        '--name swarm_cruise-0.9_r1. On macOS 27 the runner’s --minimize flag made Webots hang, so I removed it, and I shortened the '
        'run timeout to 90 s so that occasional hung runs fail fast.',
        'Part A: swarm, 120 s, default parameters and cruise = 0.9, repeated up to 5 times each (Table 7.1).',
        'Part B: Pioneer, 180 s, default parameters, 3 runs (Table 7.2, Figure 7.3). A bubble = 0.15 run was started but did not '
        'complete.',
        'Exercises from GUIDE.md §10: (1) cruise = 0.2, 0.4, 0.6 and 0.8 for the swarm, up to 3 complete runs each (Table 7.3, '
        'Figure 7.4; the cruise = 1.0 runs did not complete); '
        '(5) lidar noise 0.001 and 0.003, for which I added a --lidar-noise option to the runner, but these runs did not complete.',
        'Computed metrics and mean ± SD with my exp07-webots/analyse.py, which uses the same definitions as analysis/metrics.py.',
    ],
    code_intro='Key part of the code: my metric function (exp07-webots/analyse.py). The robot controllers were used unchanged; '
               'the two changes to tools/run_experiment.py are listed in exp07-webots/NOTES.md:',
    code=find_lines('exp07-webots/analyse.py', 'def metrics', '    return robots, 100 * len(visited) / n**2'),
    observations=[
        ('table', ('Table 7.1', 'Part A, e-puck swarm (120 s runs, repeats per setting)'),
         ['Setting', 'Run', 'Mean path per robot (m)', 'Mean speed (m/s)', 'Stuck (%) mean (worst robot)', 'Coverage (%)'],
         swarm_rows or [['(runs pending)', '', '', '', '', '']], [1.9, 0.5, 1, 1, 1.5, 0.9]),
        ('table', ('Table 7.2', 'Part B, Pioneer 3-DX with lidar (180 s runs)'),
         ['Parameter setting', 'Runs', 'Path (m)', 'Stuck (%)', 'Coverage (%)', 'Behaviour observed'],
         pio_rows or [['(runs pending)', '', '', '', '', '']], [1.1, 0.5, 0.9, 0.9, 0.9, 2.6]),
        ('table', ('Table 7.3', 'Exercises attempted (two from GUIDE.md, Section 10)'), ['Exercise no.', 'Change made', 'Measured effect'],
         ex_rows or [['(runs pending)', '', '']], [0.9, 1.6, 3.4]),
    ],
    results=[
        *([('fig', shot[0], ('Figure 7.1', 'Screenshot of the swarm arena world running in Webots (my screen)'), 14)] if shot else
          [('para', '[[Insert Figure 7.1: your own screenshot of swarm_arena.wbt running in Webots]]')]),
        ('fig', FIG7 / 'fig7_2_swarm_trajectories.png', ('Figure 7.2', 'Swarm trajectories and coverage, default parameters, 120 s (my GUI run)'), 15),
        ('fig', FIG7 / 'fig7_3_pioneer_default.png', ('Figure 7.3', 'Pioneer trajectory in the 8 m × 8 m room, default parameters, 180 s'), 15),
        ('fig', FIG7 / 'fig7_4_ex1_speed_vs_safety.png', ('Figure 7.4', 'Result plot for exercise 1: coverage and worst-robot stuck time against cruise speed'), 13),
    ],
    discussion=[],
    answers=[],
    conclusion='',
)
for item in list(E7['results']):
    if item[0] == 'fig' and not Path(item[1]).exists():
        E7['results'].remove(item)

# ---- Exp 7 prose depends on the measured numbers; filled in by exp7_text.py
from exp7_text import fill as _fill7  # noqa: E402
_fill7(E7, agg7, ms, nrep, runs7)

EXPERIMENTS = [E1, E2, E3, E4, E5, E6, E7, E8]

REFERENCES = [
    'C. R. Harris et al., “Array programming with NumPy,” Nature, vol. 585, pp. 357–362, 2020.',
    'P. Virtanen et al., “SciPy 1.0: Fundamental algorithms for scientific computing in Python,” Nature Methods, vol. 17, pp. 261–272, 2020.',
    'J. D. Hunter, “Matplotlib: A 2D graphics environment,” Computing in Science & Engineering, vol. 9, no. 3, pp. 90–95, 2007.',
    'R. R. Shivwanshi, “CSAI4014 Algorithms for Intelligent Systems and Robotics: Laboratory Manual, Experiments 1 to 6,” School of Computer Science, UPES, Dehradun, India, 2026.',
    'A. V. Oppenheim and R. W. Schafer, Discrete-Time Signal Processing, 3rd ed. Upper Saddle River, NJ, USA: Pearson, 2010.',
    'S. Russell and P. Norvig, Artificial Intelligence: A Modern Approach, 4th ed. Hoboken, NJ, USA: Pearson, 2021.',
    'R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed. Cambridge, MA, USA: MIT Press, 2018.',
    'D. E. Rumelhart, G. E. Hinton, and R. J. Williams, “Learning representations by back-propagating errors,” Nature, vol. 323, pp. 533–536, 1986.',
    'O. Michel, “Webots: Professional mobile robot simulation,” Int. J. Advanced Robotic Systems, vol. 1, no. 1, pp. 39–42, 2004.',
    'R. R. Shivwanshi, “webots-robotics-sim: Webots robotics simulations” (README.md and GUIDE.md), GitHub repository, 2026. [Online]. Available: https://github.com/reshamrajs/webots-robotics-sim',
    'V. Braitenberg, Vehicles: Experiments in Synthetic Psychology. Cambridge, MA, USA: MIT Press, 1984.',
    'V. Sezer and M. Gokasan, “A novel obstacle avoidance algorithm: Follow the gap method,” Robotics and Autonomous Systems, vol. 60, no. 9, pp. 1123–1134, 2012.',
    'E. Coumans and Y. Bai, “PyBullet, a Python module for physics simulation for games, robotics and machine learning,” 2016–2024. [Online]. Available: http://pybullet.org',
    'R. R. Shivwanshi, “Lab Manual: Cross-Embodiment Transfer of a Manipulation Skill,” AISR-Cross-Embodiment-PyBullet (MANUAL.md), UPES, Dehradun, India, 2026.',
    'Open X-Embodiment Collaboration, “Open X-Embodiment: Robotic learning datasets and RT-X models,” in Proc. IEEE Int. Conf. Robotics and Automation (ICRA), 2024.',
    'M. Laskey, J. Lee, R. Fox, A. Dragan, and K. Goldberg, “DART: Noise injection for robust imitation learning,” in Proc. Conf. Robot Learning (CoRL), 2017.',
    'S. Ross, G. Gordon, and D. Bagnell, “A reduction of imitation learning and structured prediction to no-regret online learning,” in Proc. AISTATS, 2011.',
]

APPENDIX_A = [
    ['GitHub repository', PERSON['github']],
    ['Operating system and CPU', 'macOS 27 (Darwin 27.0), Apple M5'],
    ['Python and libraries (Exp. 1–6)', 'Python 3.12.16, NumPy 2.5.5, SciPy 1.18.1, Matplotlib 3.11.2, JupyterLab; notebooks built and executed with tools/build_nb.py'],
    ['Webots (Exp. 7)', 'Webots R2025a nightly build 24/11/2026 (release R2025a does not start on macOS 27); controllers run with Python 3.15'],
    ['PyBullet environment (Exp. 8)', 'Python 3.11.16 venv, PyBullet 3.2.7 (built from source, CFLAGS="-Dfdopen=fdopen"), NumPy 2.4.6, scikit-learn 1.9.1'],
    ['Reproduce', 'pip install -r requirements.txt; python tools/build_nb.py exp0*/exp0*.py; Exp. 7 and 8 commands in each NOTES.md'],
]
REPO_LAYOUT = '''aisr-lab-<SAP ID>/
  README.md            name, SAP ID, batch, partner, sources, AI tools
  requirements.txt     tools/build_nb.py   tools/summarise.py   OBSERVATIONS.md
  exp01-signals/       exp01.py  exp01.ipynb  obs.json  figs/
  exp02-queens/        exp02.py  exp02.ipynb  obs.json  figs/
  exp03-search/        exp03.py  exp03.ipynb  obs.json  figs/
  exp04-hillclimb/     exp04.py  exp04.ipynb  obs.json  figs/
  exp05-rl/            exp05.py  exp05.ipynb  obs.json  figs/
  exp06-neural/        exp06.py  exp06.ipynb  obs.json  figs/
  exp07-webots/        analyse.py  controllers/ (changed files)  runs/*.csv  figs/  NOTES.md
  exp08-xembody/       results/*.csv  figs/  exercises/e4_scale_sweep.py  NOTES.md
  report/              build.py  content.py  (this report)'''
APPENDIX_B_INTRO = ('The Lab Manual permits reference material and AI assistants on the condition that every line submitted can be '
                    'explained and modified, and that every source is named. The sources and tools I used are listed below.')
APPENDIX_B = [
    ['1–6', 'CSAI4014 Laboratory Manual [4]', 'Experiment design, parameters and example code, which my notebooks adapt'],
    ['1', 'Oppenheim and Schafer [5]; SciPy docs [2]', 'Sampling, aliasing and leakage; solve_ivp usage'],
    ['2–4', 'Russell and Norvig [6]', 'CSP formulation, BFS/DFS properties, hill climbing and restarts'],
    ['5', 'Sutton and Barto [7]', 'Q-learning update and off-policy learning'],
    ['6', 'Rumelhart et al. [8]', 'Backpropagation'],
    ['7', 'webots-robotics-sim README/GUIDE [10]; Webots issue 6976', 'Controllers, runner and metrics; the macOS 27 fix (nightly build)'],
    ['8', 'Cross-embodiment manual and code [14]', 'All Part 1–5 scripts (unchanged); exercises E1 and E4'],
    ['1–8', 'Claude (Anthropic), AI assistant', 'Helped write and debug the experiment scripts, analysis and plotting code, the E4 and '
     'Exp 7 analysis scripts, the Webots/PyBullet installation fixes, and drafted report text and question answers from my '
     'measured results. I have checked the results and can explain every line.'],
]
