#!python3
import argparse
import os
from collections import defaultdict
from math import ceil

import pandas as pd
from numpy import lcm

list_t_size = 20
listItem_t_size = 20
tcb_t_size = 336
pointer_size = 4


def compute_size(lines: str, lazytick: bool, harmonic: bool, table: bool):
    td = lines[3]

    tds = [s.lstrip(r'{').rstrip(r'}') for s in td.split('=')[1][2:-2].split(r'},')]
    tuples = [s.split(',') for s in tds]

    timers = {i: int(t) for i, t in enumerate(lines[2].split('=')[1][2:-3].split(','))}
    # need to distinguish harmonic and generic

    # ringbuffer max is per timer: num_slot*size(list_t) + num_tasks*size(listitem) + num_tasks*size(tcb_t)
    # harmonic max is per timer: num_tasks*size(listitem) + num_tasks*size(tcb_t)
    # freertos&oneshot is same => max is num_tasks*size(listitem)
    task_to_timer = defaultdict(list)
    for t in tuples:
        task_to_timer[int(t[0])].append(int(t[1]))

    task_periods = [int(t[1]) for t in tuples]
    # print(task_to_timer)
    num_tasks = len(tuples)
    num_timers = len(timers)
    size = num_tasks*tcb_t_size
    if table:
        hyperperiod = lcm.reduce(task_periods)
        for t in tuples:  # num tcbs
            period = int(t[1])
            num_releases = hyperperiod/period
            size += pointer_size*num_releases
        num_ticks = set()
        for t in tuples:  # |\mathcal{J}|
            period = int(t[1])
            ticks = [tick for tick in range(1, hyperperiod+1) if tick % period == 0]
            for tick in ticks:
                num_ticks.add(tick)
        size += pointer_size*len(num_ticks)
    elif lazytick and not harmonic:
        ringbuffer_slots = {}
        for t in timers.keys():
            ringbuffer_slots[t] = (ceil(max(task_to_timer[t])/timers[t]), len(task_to_timer[t]))
        size += num_timers*pointer_size+(num_tasks*pointer_size)
        for t in timers.keys():
            size += ringbuffer_slots[t][0]*list_t_size
    elif lazytick and harmonic:
        size += num_timers*pointer_size+(num_tasks*pointer_size) # array per timer + pointers to all tasks
    elif not lazytick:
        size += list_t_size+(pointer_size*num_tasks)  # only one list + pointers to all tasks
    return size


parser = argparse.ArgumentParser(description="Parse dir")
parser.add_argument("--dir", type=str, required=True)
args = parser.parse_args()

sizes = defaultdict(list)

for test in ['td-generic', 'td-harmonic']:
    for f in sorted(os.listdir(os.path.join(os.path.abspath(args.dir), test))):
        if f.endswith('.h'):
            continue
        if any([s in f for s in ['t100', 't200', 't300', 't400', 't500']]) and 'tim4' in f:
            with open(os.path.abspath(os.path.join(os.path.abspath(args.dir), test, f)), 'r') as file:
                lines = file.readlines()
            # print((test, f.split('-')[1], f.split('-')[2]))
            table = compute_size(lines, lazytick=False, harmonic=False, table=True)
            freertos = compute_size(lines, lazytick=False, harmonic=(test == "td-harmonic"), table=False)
            # print(f'freertos: {freertos}')
            lazytick = compute_size(lines, lazytick=True, harmonic=(test == "td-harmonic"), table=False)
            # print(f'lazytick: {lazytick}')
            sizes[(test, 'freertos')].append(f'\SI{{{format(freertos/1000, ".2f")}}}{{\kilo\\byte}}')
            sizes[(test, 'lazytick')].append(f'\SI{{{format(lazytick/1000, ".2f")}}}{{\kilo\\byte}}')
            sizes[(test, 'table')].append(f'\SI{{{format(table/1000000, ".2f")}}}{{\mega\\byte}}')

print(sizes)
sizes_out = []
a = ['FreeRTOS']
a.extend(sizes[('td-generic', 'freertos')])
sizes_out.append(a)
a = ['LazyTick (harmonic)']
a.extend(sizes[('td-harmonic', 'lazytick')])
sizes_out.append(a)
a = ['LazyTick (non-harmonic)']
a.extend(sizes[('td-generic', 'lazytick')])
sizes_out.append(a)
a = ['Table-driven (harmonic)']
a.extend(sizes[('td-harmonic', 'table')])
sizes_out.append(a)
a = ['Table-driven (non-harmonic)']
a.extend(sizes[('td-generic', 'table')])
sizes_out.append(a)

print(sizes_out)

df = pd.DataFrame(sizes_out, columns=['Test scenario', '100 tasks', '200 tasks', '300 tasks', '400 tasks', '500 tasks'])

print(df.to_latex(index=False))
