#!python3
import argparse
import os

import pandas as pd

parser = argparse.ArgumentParser(description="Parse results")
parser.add_argument("--res", type=str, required=True)
args = parser.parse_args()

results_csv = os.path.abspath(args.res)

df = pd.read_csv(results_csv)
df.drop(df[df.taskset == 'hybrid'].index, inplace=True)  # ignore hybrid tests

grouped = df.groupby(['test_type', 'taskset', 'num_timers'])
out_dir = os.path.abspath(f'results-split')
if not os.path.exists(out_dir):
    os.makedirs(out_dir)


# sanity check
sanity_group = df.groupby(['taskset', 'num_timers', 'num_tasks'])[['test_type', 'taskset', 'num_tasks', 'insert_counter']]
insert_differ = []
for name, df in sanity_group:
    uniques = pd.unique(df['insert_counter'])
    if len(pd.unique(df['insert_counter'])) != 1:
        insert_differ.append((name, df))
if insert_differ != []:
    print(f'Insert count differs:')
    for d in insert_differ:
        print(d)


for name, group in grouped:
    name = '_'.join([str(n) for n in name])
    group.to_csv(os.path.join(out_dir, f'{name}.csv'), index=False)
