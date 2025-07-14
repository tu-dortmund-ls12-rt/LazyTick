#!python3
import argparse
import functools as ft
import os
from math import ceil

import pandas as pd

parser = argparse.ArgumentParser(description="Parse res")
parser.add_argument("--res", type=str, required=True)
args = parser.parse_args()

df = pd.read_csv(os.path.abspath(args.res))
grouped = df.groupby(['test_type', 'taskset'])
dfs_harmonic = []
dfs_generic = []
for n, g in grouped:
    d = g[['test_type', 'num_timers', 'num_tasks', 'insert_sum', 'retrieval_sum', 'runtime_isr', 'insert_counter', 'retrieval_counter', 'count_isr']]
    if n[1] == 'generic':
        dfs_generic.append(d)
    elif n[1] == 'harmonic':
        dfs_harmonic.append(d)

harmonic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_harmonic)

generic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_generic)

summary = []

harmonic['insert_per_freertos'] = harmonic['insert_sum_x']/harmonic['insert_counter_x']
harmonic['insert_per_oneshot'] = harmonic['insert_sum']/harmonic['insert_counter']
harmonic['insert_per_lazytick'] = harmonic['insert_sum_y']/harmonic['insert_counter_y']
harmonic['retrieval_per_freertos'] = harmonic['retrieval_sum_x']/harmonic['retrieval_counter_x']
harmonic['retrieval_per_oneshot'] = harmonic['retrieval_sum']/harmonic['retrieval_counter']
harmonic['retrieval_per_lazytick'] = harmonic['retrieval_sum_y']/harmonic['retrieval_counter_y']
harmonic['isr_per_freertos'] = (harmonic['runtime_isr_x']-harmonic['retrieval_sum_x'])/harmonic['count_isr_x']
harmonic['isr_per_oneshot'] = (harmonic['runtime_isr']-harmonic['retrieval_sum'])/harmonic['count_isr']
harmonic['isr_per_lazytick'] = (harmonic['runtime_isr_y']-harmonic['retrieval_sum_y'])/harmonic['count_isr_y']

# harmonic = harmonic[['num_timers', 'num_tasks', 'insert_per_freertos', 'insert_per_oneshot', 'insert_per_lazytick', 'retrieval_per_freertos', 'retrieval_per_oneshot', 'retrieval_per_lazytick', 'isr_per_freertos', 'isr_per_oneshot', 'isr_per_lazytick']]
summary.append(['FreeRTOS (harmonic)', harmonic['insert_per_freertos'].max(), harmonic['insert_per_freertos'].mean(),
                # harmonic['retrieval_per_freertos'].max(), harmonic['retrieval_per_freertos'].mean(),
                harmonic['isr_per_freertos'].max(), harmonic['isr_per_freertos'].mean()])
summary.append(['One-shot (harmonic)', harmonic['insert_per_oneshot'].max(), harmonic['insert_per_oneshot'].mean(),
                # harmonic['retrieval_per_oneshot'].max(), harmonic['retrieval_per_oneshot'].mean(),
                harmonic['isr_per_oneshot'].max(), harmonic['isr_per_oneshot'].mean()])
summary.append(['LazyTick (harmonic)', harmonic['insert_per_lazytick'].max(), harmonic['insert_per_lazytick'].mean(),
                # harmonic['retrieval_per_lazytick'].max(), harmonic['retrieval_per_lazytick'].mean(),
                harmonic['isr_per_lazytick'].max(), harmonic['isr_per_lazytick'].mean()])

# generic

generic['insert_per_freertos'] = generic['insert_sum_x']/generic['insert_counter_x']
generic['insert_per_oneshot'] = generic['insert_sum']/generic['insert_counter']
generic['insert_per_lazytick'] = generic['insert_sum_y']/generic['insert_counter_y']
generic['retrieval_per_freertos'] = generic['retrieval_sum_x']/generic['retrieval_counter_x']
generic['retrieval_per_oneshot'] = generic['retrieval_sum']/generic['retrieval_counter']
generic['retrieval_per_lazytick'] = generic['retrieval_sum_y']/generic['retrieval_counter_y']
generic['isr_per_freertos'] = (generic['runtime_isr_x']-generic['retrieval_sum_x'])/generic['count_isr_x']
generic['isr_per_oneshot'] = (generic['runtime_isr']-generic['retrieval_sum'])/generic['count_isr']
generic['isr_per_lazytick'] = (generic['runtime_isr_y']-generic['retrieval_sum_y'])/generic['count_isr_y']

# generic = generic[['num_timers', 'num_tasks', 'insert_per_freertos', 'insert_per_oneshot', 'insert_per_lazytick', 'retrieval_per_freertos', 'retrieval_per_oneshot', 'retrieval_per_lazytick', 'isr_per_freertos', 'isr_per_oneshot', 'isr_per_lazytick']]
summary.append(['FreeRTOS (generic)', generic['insert_per_freertos'].max(), generic['insert_per_freertos'].mean(),
                # generic['retrieval_per_freertos'].max(), generic['retrieval_per_freertos'].mean(),
                generic['isr_per_freertos'].max(), generic['isr_per_freertos'].mean()])
summary.append(['One-shot (generic)', generic['insert_per_oneshot'].max(), generic['insert_per_oneshot'].mean(),
                # generic['retrieval_per_oneshot'].max(), generic['retrieval_per_oneshot'].mean(),
                generic['isr_per_oneshot'].max(), generic['isr_per_oneshot'].mean()])
summary.append(['LazyTick (generic)', generic['insert_per_lazytick'].max(), generic['insert_per_lazytick'].mean(),
                # generic['retrieval_per_lazytick'].max(), generic['retrieval_per_lazytick'].mean(),
                generic['isr_per_lazytick'].max(), generic['isr_per_lazytick'].mean()])


df = pd.DataFrame(summary, columns=['Test scenario', 'peak', 'mean', 'peak','mean'])
print(df.to_latex(index=False,float_format="$%.0f$"))