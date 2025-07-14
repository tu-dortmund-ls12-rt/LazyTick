#!python3
import argparse
import functools as ft
import os

import pandas as pd


parser = argparse.ArgumentParser(description="Parse res")
parser.add_argument("--res", type=str, required=True)
args = parser.parse_args()

df = pd.read_csv(os.path.abspath(args.res))
grouped = df.groupby(['test_type', 'taskset'])
dfs_harmonic = []
dfs_generic = []
for n, g in grouped:
    d = g[['test_type', 'num_timers', 'num_tasks', 'insert_span', 'retrieval_span', 'isr_span', 'combined_overhead','insert_sum','runtime_isr']]
    if n[1] == 'generic':
        dfs_generic.append(d)
    elif n[1] == 'harmonic':
        dfs_harmonic.append(d)

harmonic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_harmonic)

generic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_generic)

max_insert_isr_relation = []
for d in dfs_harmonic + dfs_generic:
    max_insert_isr_relation.append(max(d['insert_sum'] / d['runtime_isr']))
    # print(d)
print(f'max insert relation: {max(max_insert_isr_relation)}')

summary = []

harmonic['insert_diff_freertos'] = harmonic['insert_span_x']/harmonic['insert_span_y']
harmonic['insert_diff_oneshot'] = harmonic['insert_span']/harmonic['insert_span_y']
harmonic['retrieval_diff_freertos'] = harmonic['retrieval_span_x']/harmonic['retrieval_span_y']
harmonic['retrieval_diff_oneshot'] = harmonic['retrieval_span']/harmonic['retrieval_span_y']
harmonic['overhead_diff_freertos'] = harmonic['combined_overhead_x']/harmonic['combined_overhead_y']
harmonic['overhead_diff_oneshot'] = harmonic['combined_overhead']/harmonic['combined_overhead_y']
harmonic = harmonic[['num_timers', 'num_tasks', 'insert_diff_freertos', 'insert_diff_oneshot', 'retrieval_diff_freertos', 'retrieval_diff_oneshot', 'overhead_diff_freertos', 'overhead_diff_oneshot']]
summary.append(['FreeRTOS (harmonic)', harmonic['insert_diff_freertos'].max(), harmonic['insert_diff_freertos'].mean(),
                harmonic['retrieval_diff_freertos'].max(), harmonic['retrieval_diff_freertos'].mean(),
                harmonic['overhead_diff_freertos'].max(), harmonic['overhead_diff_freertos'].mean()])
summary.append(['One-shot (harmonic)', harmonic['insert_diff_oneshot'].max(), harmonic['insert_diff_oneshot'].mean(),
                harmonic['retrieval_diff_oneshot'].max(), harmonic['retrieval_diff_oneshot'].mean(),
                harmonic['overhead_diff_oneshot'].max(), harmonic['overhead_diff_oneshot'].mean()])

# generic
generic['insert_diff_freertos'] = generic['insert_span_x']/generic['insert_span_y']
generic['insert_diff_oneshot'] = generic['insert_span']/generic['insert_span_y']
generic['retrieval_diff_freertos'] = generic['retrieval_span_x']/generic['retrieval_span_y']
generic['retrieval_diff_oneshot'] = generic['retrieval_span']/generic['retrieval_span_y']
generic['overhead_diff_freertos'] = generic['combined_overhead_x']/generic['combined_overhead_y']
generic['overhead_diff_oneshot'] = generic['combined_overhead']/generic['combined_overhead_y']
generic = generic[['num_timers', 'num_tasks', 'insert_diff_freertos', 'insert_diff_oneshot', 'retrieval_diff_freertos', 'retrieval_diff_oneshot', 'overhead_diff_freertos', 'overhead_diff_oneshot']]

summary.append(['FreeRTOS (generic)', generic['insert_diff_freertos'].max(), generic['insert_diff_freertos'].mean(),
                generic['retrieval_diff_freertos'].max(), generic['retrieval_diff_freertos'].mean(),
                generic['overhead_diff_freertos'].max(), generic['overhead_diff_freertos'].mean()])
summary.append(['One-shot (generic)', generic['insert_diff_oneshot'].max(), generic['insert_diff_oneshot'].mean(),
                generic['retrieval_diff_oneshot'].max(), generic['retrieval_diff_oneshot'].mean(),
                generic['overhead_diff_oneshot'].max(), generic['overhead_diff_oneshot'].mean()])


df = pd.DataFrame(summary, columns=['Test scenario', 'peak', 'mean', 'peak', 'mean', 'peak','mean'])
print(df.to_latex(index=False,float_format="$%.2f\\times$"))
# sizes = defaultdict(list)

# for test in ['td-generic', 'td-harmonic']:
#     for f in sorted(os.listdir(os.path.join(os.path.abspath(args.dir), test))):
#         if f.endswith('.h'):
#             continue
#         if any([s in f for s in ['t100', 't200', 't300', 't400', 't500']]) and 'tim4' in f:
#             with open(os.path.abspath(os.path.join(os.path.abspath(args.dir), test, f)), 'r') as file:
#                 lines = file.readlines()
#             # print((test, f.split('-')[1], f.split('-')[2]))
#             freertos = compute_size(lines, lazytick=False, harmonic=(test == "td-harmonic"))
#             # print(f'freertos: {freertos}')
#             lazytick = compute_size(lines, lazytick=True, harmonic=(test == "td-harmonic"))
#             # print(f'lazytick: {lazytick}')
#             sizes[(test, 'freertos')].append(f'\SI{{{format(freertos/1000, ".2f")}}}{{\kilo\\byte}}')
#             sizes[(test, 'lazytick')].append(f'\SI{{{format(lazytick/1000, ".2f")}}}{{\kilo\\byte}}')

# print(sizes)
# sizes_out = []
# a =['FreeRTOS']
# a.extend(sizes[('td-generic', 'freertos')])
# sizes_out.append(a)
# a =['LazyTick (harmonic)']
# a.extend(sizes[('td-harmonic', 'lazytick')])
# sizes_out.append(a)
# a =['LazyTick (generic)']
# a.extend(sizes[('td-generic', 'lazytick')])
# sizes_out.append(a)

# print(sizes_out)

# df = pd.DataFrame(sizes_out, columns=['Test scenario', '100 tasks', '200 tasks', '300 tasks', '400 tasks', '500 tasks'])

# print(df.to_latex(index=False))
