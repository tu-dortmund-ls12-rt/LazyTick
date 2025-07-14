#!python3
import argparse
import os
from collections import defaultdict

parser = argparse.ArgumentParser(description="Parse freertos compare")
parser.add_argument("--freertos", type=str, required=True)
parser.add_argument("--compare", type=str, required=False)
args = parser.parse_args()

file_freertos = os.path.abspath(args.freertos)
file_compare = os.path.abspath(args.compare)

with open(file_freertos, 'r') as f:
    lines_freertos = f.readlines()
with open(file_compare, 'r') as f:
    lines_compare = f.readlines()


inserts_freertos = [l.split(':')[1].strip().split(',') for l in lines_freertos if 'insert:' in l]

inserts_freertos = [(l[0].strip(), int(l[1].split('tick')[1].strip()[:-4])) for l in inserts_freertos]


inserts_freertos_dict = defaultdict(list)
for task, tick in inserts_freertos:
    inserts_freertos_dict[task].append(tick)


inserts_compare = [l.split(':')[1].strip().split(',') for l in lines_compare if 'insert:' in l]

inserts_compare = [(l[0].strip(), int(l[1].split('tick')[1].strip()[:-4])) for l in inserts_compare]


inserts_compare_dict = defaultdict(list)
for task, tick in inserts_compare:
    inserts_compare_dict[task].append(tick)

for k in inserts_freertos_dict.keys():
    f = sorted(inserts_freertos_dict[k])
    c = sorted(inserts_compare_dict[k])
    if len(f) != len(c):
        print(f'inserts of task {k} differ:')
        print(f)
        print(c)
