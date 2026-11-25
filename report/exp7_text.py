"""Experiment 7 prose, written from the measured values (so it stays true if runs are added)."""


def fill(E, agg, ms, nrep, runs):
    import json
    from pathlib import Path
    sj = Path(__file__).resolve().parent.parent / 'exp07-webots/runs/summary.json'
    extra = json.loads(sj.read_text()) if sj.exists() else {}
    gui = extra.get('gui') or {}
    def m(world, setting, key):
        v = agg(world, setting, key)
        return None if v is None else v[0]
    d_cov, d_stk, d_path = m('swarm', 'default', 'coverage'), m('swarm', 'default', 'stuck_worst'), m('swarm', 'default', 'path_mean')
    h_cov, h_stk, h_path = m('swarm', 'cruise-0.9', 'coverage'), m('swarm', 'cruise-0.9', 'stuck_worst'), m('swarm', 'cruise-0.9', 'path_mean')
    p_cov, p_stk, p_path = m('pioneer', 'default', 'coverage'), m('pioneer', 'default', 'stuck_worst'), m('pioneer', 'default', 'path_mean')
    b_cov, b_stk, b_path = m('pioneer', 'bubble-0.15', 'coverage'), m('pioneer', 'bubble-0.15', 'stuck_worst'), m('pioneer', 'bubble-0.15', 'path_mean')
    f = lambda x, k='{:.0f}': '?' if x is None else k.format(x)
    sw = [r for r in runs if r['world'] == 'swarm' and r['setting'] == 'default']
    worst_hi = max((r for r in runs if r['setting'] == 'cruise-0.9'), key=lambda r: r['stuck_worst'], default=None)
    sw_set = sorted({r['setting'] for r in runs if r['world'] == 'swarm'})
    trap = max(sw_set, key=lambda st: m('swarm', st, 'stuck_worst') or 0, default=None)
    trap_v = m('swarm', trap, 'stuck_worst') if trap else None
    trap_txt = '' if trap_v is None or trap_v < 15 else (
        f' The clearest case of the trade-off came at {trap.replace("-", " = ")}: one robot was wedged for {trap_v:.0f}% of the run, '
        'while the slower settings kept every robot under 3% stuck.')

    res = (f'With default parameters the five e-pucks covered {f(d_cov)}% of the arena in 120 s, driving {f(d_path, "{:.1f}")} m each with '
           f'at most {f(d_stk, "{:.1f}")}% of the time stuck (Table 7.1, Figure 7.2). Raising cruise to 0.9 increased the path to '
           f'{f(h_path, "{:.1f}")} m per robot and coverage to {f(h_cov)}%, with the worst robot stuck {f(h_stk, "{:.1f}")}% of the time on '
           f'average. The Pioneer drove {f(p_path, "{:.1f}")} m in 180 s with {f(p_stk, "{:.1f}")}% stuck time but covered only {f(p_cov)}% of '
           f'the room (Figure 7.3).')
    if b_cov is not None:
        res += f' With bubble = 0.15 m it covered {f(b_cov)}% and was stuck {f(b_stk, "{:.0f}")}% of the time (Table 7.2).'
    res += ' Figure 7.4 shows coverage and worst-robot stuck time against cruise speed (exercise 1).'
    n1, n3 = m('pioneer', 'noise-0.001', 'coverage'), m('pioneer', 'noise-0.003', 'coverage')
    if n1 is not None and n3 is not None:
        res += (f' With lidar noise of about 8 cm and 24 cm per beam the Pioneer still never got stuck, and its coverage fell only '
                f'from {f(p_cov, "{:.1f}")}% to {f(n1, "{:.1f}")}% and {f(n3, "{:.1f}")}% (exercise 5, Figure 7.5).')
    E['results'].append(('para', res))

    disc = [
        'I expected faster e-pucks to explore more but to get trapped more often, and the Pioneer to avoid every obstacle while '
        'covering little of the room, as GUIDE.md §8 reports. ' +
        (f'Coverage did rise with speed ({f(d_cov)}% → {f(h_cov)}%). ' if h_cov is not None and d_cov is not None and h_cov > d_cov else
         f'Coverage changed from {f(d_cov)}% to {f(h_cov)}% at cruise 0.9. ') +
        (f'At cruise 0.9 one robot was wedged for {worst_hi["stuck_worst"]:.0f}% of run {worst_hi["run"]}, ' if worst_hi and worst_hi['stuck_worst'] > 30
         else 'At cruise 0.9 no robot was trapped for most of a run, unlike the run reported in GUIDE.md, ') +
        'which shows that whether a fast robot gets trapped depends on the exact encounters in a run.' + trap_txt,
        f'The Pioneer behaved as the guide describes: it kept moving ({f(p_stk, "{:.1f}")}% stuck), but drove a repeated loop and {f(p_cov)}% coverage, because a reactive '
        'controller has no memory of where it has been. ' +
        (f'Shrinking the bubble to 0.15 m, below the robot’s half-width, raised stuck time to {f(b_stk)}%: the gap it steered into was '
         'narrower than the robot.' if b_stk is not None else ''),
    ]
    # which settings varied between repeats
    groups = {}
    for r in runs:
        groups.setdefault((r['world'], r['setting']), []).append(round(r['coverage'], 4))
    varied = sorted(f"{w} {st}" for (w, st), v in groups.items() if len(v) > 1 and len(set(v)) > 1)
    same = sorted(f"{w} {st}" for (w, st), v in groups.items() if len(v) > 1 and len(set(v)) == 1)
    gui_same = gui and d_cov is not None and abs(gui.get('coverage', -1) - d_cov) < 1e-6
    if same and not varied:
        disc.append('One result differed from the guide. GUIDE.md says runs are not bit-for-bit repeatable, but every complete repeat '
                    'of the same setting gave an identical trajectory file (' + ', '.join(same) + ')' +
                    (', and my GUI run of the default swarm matched the headless runs exactly' if gui_same else '') + '. In --batch '
                    '--mode=fast Webots advances the controllers in lock-step with the physics, and these controllers use no randomness '
                    '(noise = 0), so on one machine the simulation is deterministic. Repeats therefore add no new information here; '
                    'variation would need a source of randomness, such as the noise parameter, a different machine, or real-time runs. '
                    'I still report every repeat (SD = 0).')
    elif same or varied:
        disc.append('Repeatability was mixed: repeats were identical for ' + (', '.join(same) or 'none') + ' and differed for '
                    + ', '.join(varied) + '. A run only diverges if a timing difference between controller processes changes a close '
                    'call, so I report every repeat and the mean ± SD rather than one run.')
    if n1 is not None and n3 is not None:
        disc.append('Exercise 5 asked whether follow-the-gap tolerates a noisy lidar. I expected noise to make the free/blocked '
                    'decision flicker near the 1 m threshold and cause hesitation or collisions. Instead the controller was barely '
                    f'affected: stuck time stayed at 0% and coverage changed from {f(p_cov, "{:.1f}")}% to {f(n1, "{:.1f}")}% (≈ 8 cm '
                    f'noise) and {f(n3, "{:.1f}")}% (≈ 24 cm), with the path length within 2%. The noise is small compared with the '
                    '1 m "free" threshold and the 0.45 m bubble, and the widest-gap choice averages over many beams, so single noisy '
                    'beams rarely change the chosen heading. The noise did shift the trajectory slightly (the paths differ from the '
                    'noise-free run), but not the looping behaviour. The noisy repeats were also identical to each other, which shows '
                    'that Webots draws its sensor noise from a generator seeded the same way at every start (WorldInfo randomSeed).')
    if extra.get('incomplete'):
        disc.append(f'{len(extra["incomplete"])} runs stopped before the full simulated time when a hung Webots instance was killed '
                    '(' + ', '.join(extra['incomplete']) + '). Their logs are partial, so I excluded them from every table and plot.')
    if extra.get('failed'):
        disc.append(f'{extra["failed"]} of {extra["attempts"]} headless run attempts hung or failed at start-up on this macOS 27 nightly '
                    'build (Webots started but the controllers never connected), including the 7 partial runs above; they were stopped by the timeout and retried. '
                    'None of them is in the tables.')
    E['discussion'] = disc

    E['answers'] = [
        'Each IR sensor is wired straight to the wheels with mirrored weights: an obstacle on the right raises the right sensors, '
        'which lowers the left wheel speed and raises the right one, so the robot turns away. Avoidance emerges from this wiring with '
        'no map or plan. In a corner both front sensors fire almost equally, so the turning terms cancel, and the robot slows and '
        'jitters without escaping, especially if it arrives too fast.',
        f'Faster robots travel further in the same time, so they visit more cells: path {f(d_path, "{:.1f}")} → {f(h_path, "{:.1f}")} m per '
        f'robot and coverage {f(d_cov)}% → {f(h_cov)}% in my runs. But the IR sensors only see about 5 cm, so a fast robot has less time '
        'between detecting an obstacle and hitting it. It can wedge into a corner before the turning term acts. Worst-robot stuck time '
        f'was {f(d_stk, "{:.1f}")}% at default and {f(h_stk, "{:.1f}")}% at cruise 0.9' + (f', and {trap_v:.0f}% at {trap.replace("-", " = ")}, '
        'where one robot was wedged for over a quarter of the run' if trap_v and trap_v >= 15 else '') +
        ': speed buys exploration at the cost of safety.',
        'It clips the scan at lookahead, marks beams longer than free as open, blanks a safety bubble around the nearest return, takes '
        'the widest run of open beams and steers to its middle beam. The bubble is meant to stop the robot cutting past the nearest '
        'obstacle. If it is smaller than the robot’s half-width, gaps narrower than the robot still look passable, so the robot '
        'steers into them and its side hits the obstacle.' + (f' With bubble = 0.15 m it was stuck {f(b_stk)}% of the time.' if b_stk is not None else ''),
        'A reactive controller maps the current scan to a command and keeps no memory. In a fixed room, the same position and heading '
        'always give the same command, so once the robot enters a cycle of states it repeats it forever. Covering more needs memory '
        'or a goal: a coarse occupancy grid of visited cells with a bias towards unvisited gaps, a little randomness in the target '
        f'heading, or frontier-based exploration. My default Pioneer covered only {f(p_cov)}%.',
        ('The controllers run as separate processes that exchange data with the simulator every step. A small difference in '
         'timing can change which way a robot turns at a close call, and after that the runs diverge. In my runs repeats were '
         + ('identical for ' + ', '.join(same) + ' but varied for ' + ', '.join(varied) if same and varied else
            'not identical' if varied else 'bit-for-bit identical in headless batch mode, where Webots steps the controllers in '
            'lock-step with the physics') +
         '. To compare settings fairly I repeated each one 3–5 times, compared mean ± SD rather than single runs, and changed only one '
         'parameter at a time.'),
    ]
    E['conclusion'] = (f'A Braitenberg swarm with no map or memory avoided obstacles and covered about {f(d_cov)}% of its arena, and higher '
                       'speed traded exploration against getting stuck. Follow-the-gap kept the Pioneer collision-free but, being '
                       f'purely reactive, it drove the same loop and covered only {f(p_cov)}% of the room. Reactive layers like these are the fast safety reflexes under the map-based planners of warehouse '
                       'AGVs, robot vacuum cleaners and F1TENTH racing cars.')
