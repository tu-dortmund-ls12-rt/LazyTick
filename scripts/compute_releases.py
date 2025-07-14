#!python3
import argparse
import os
from collections import defaultdict

parser = argparse.ArgumentParser(description="Parse td")
parser.add_argument("--td", type=str, required=True)
parser.add_argument("--log", type=str, required=False)
args = parser.parse_args()
td_file = os.path.abspath(args.td)

with open(td_file, 'r') as f:
    lines = f.readlines()

td = lines[3]

tds = [s.lstrip(r'{').rstrip(r'}') for s in td.split('=')[1][2:-2].split(r'},')]
tuples = [s.split(',') for s in tds]
tasks = {}
periods = defaultdict(list)
for i, t in enumerate(tuples):
    tasks[f't{i}'] = int(t[1])
    periods[int(t[1])].append(f't{i}')

interrupts = defaultdict(list)
releases = defaultdict(list)

for i in range(1, 100+1):
    for t in sorted(periods.keys()):
        if i % t == 0:
            interrupts[i].append(t)
            releases[i].append(periods[t])

for k, v in interrupts.items():
    print(f"{k}:\t{v}")

for k, v in releases.items():
    print(f"{k}:\t{sorted([t for l in v for t in l])}")

print(len(releases.keys()))

if args.log != None:
    with open(os.path.abspath(args.log),'r') as f:
        lines = [l for l in f.readlines() if 'E isr:' in l]
lines = [l.split(':')[1].strip().split(',') for l in lines]
log_releases_str = [(l[0].strip(),l[2].strip()) for l in lines]
log_releases = defaultdict(list)
for tick,task in log_releases_str:
    t = int(tick.split(' ')[1])
    ta = task.split(' ')[1]
    log_releases[t].append(ta)

for k, v in log_releases.items():
    # print(f"{k}:\t{sorted(v)}")
    same = sorted([t for l in releases[k] for t in l]) == sorted(log_releases[k])
    if not same:
        print(f'tick {k}:\n{sorted([t for l in releases[k] for t in l])}\n{sorted(log_releases[k])}')
if same:
    print('correct releases')