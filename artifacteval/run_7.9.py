import functools as ft
import os

import pandas as pd

CSV_FILE_LARGE = os.path.join('figures', 'results', 'logs', 'results.csv')
CSV_FILE_SMALL = os.path.join('figures', 'results-small', 'logs', 'results.csv')

TABLE_TEMPLATE = r"""
\begin{table}
    \centering
    \begin{tabular}{l<{\hspace{.5cm}}rr<{\hspace{.5cm}}rr<{\hspace{.5cm}}rr}
        \toprule
                                & \multicolumn{2}{c<{\hspace{.5cm}}}{\makecell[c]{Runtime Variability\\(insert)}} & \multicolumn{2}{c<{\hspace{.5cm}}}{\makecell[c]{Runtime Variability\\(retrieval)}} & \multicolumn{2}{c}{\makecell[c]{Combined\\Overhead}}                                              \\\cmidrule(lr{.5cm}){2-3}\cmidrule(lr{.5cm}){4-5}\cmidrule(lr){6-7}
                                & peak                                                   & mean                                                      & peak                         & mean         & peak         & mean         \\
        \midrule
        {CONTENT}
        \bottomrule
    \end{tabular}
    \vspace*{1ex}%
    \caption{Reduction of runtime variability and overhead when using \textit{LazyTick}.}\label{table:summary}
\end{table}
"""


df_large = pd.read_csv(os.path.abspath(CSV_FILE_LARGE))
df_small = pd.read_csv(os.path.abspath(CSV_FILE_SMALL))
df = pd.concat([df_large, df_small], ignore_index=True)

grouped = df.groupby(['test_type', 'taskset'])
dfs_harmonic = []
dfs_generic = []
for n, g in grouped:
    d = g[['test_type', 'num_timers', 'num_tasks', 'insert_span', 'retrieval_span', 'isr_span', 'combined_overhead', 'insert_sum', 'runtime_isr']]
    if n[1] == 'generic':
        dfs_generic.append(d)
    elif n[1] == 'harmonic':
        dfs_harmonic.append(d)

harmonic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_harmonic)

generic = ft.reduce(lambda left, right: pd.merge(left, right, on=['num_tasks', 'num_timers'], sort=True), dfs_generic)

max_insert_isr_relation = []
for d in dfs_harmonic + dfs_generic:
    max_insert_isr_relation.append(max(d['insert_sum'] / d['runtime_isr']))

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


df = pd.DataFrame(summary, columns=['Test scenario', 'peak', 'mean', 'peak', 'mean', 'peak', 'mean'])
out= df.to_latex(index=False, float_format="$%.2f\\times$")

out = "\n".join(out.splitlines()[4:-2])

tex = TABLE_TEMPLATE.replace('{CONTENT}', out)
with open(os.path.join('figures', '7.9-table.tex'), 'w') as f:
    f.write(tex)
