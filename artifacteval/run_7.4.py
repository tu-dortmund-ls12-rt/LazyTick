import os
import subprocess

import pandas as pd

NUM_TESTS = 100  # number of tests per timer count

PROJECT_PATH = os.path.abspath(os.pardir)
HELPER_PATH = os.path.join(PROJECT_PATH, 'artifacteval', 'helperscripts')
cmd = (
        f". {PROJECT_PATH}/esp-idf/export.sh && "
        "./solve_task_sets.sh"
    )
subprocess.run(cmd, shell=True, cwd=HELPER_PATH, check=True)

# eval files

files = [
    (os.path.abspath(os.path.join('helperscripts', 'td-harmonic')), 'harmonic'),
    (os.path.abspath(os.path.join('helperscripts', 'td-generic')), 'generic')]

for file, test in files:
    df = pd.read_csv(os.path.join(file, f'miqcp-eval-{test}.csv'), sep=';')
    grouped = df.groupby('Number of Timers')
    rows = []

    for name, group in grouped:
        num_rows = len(group) / NUM_TESTS
        mean_runtime = group['Model Runtime'].mean()
        rows.append({
            'num_timers': name,
            'success_rate': num_rows,
            'mean_runtime': mean_runtime
        })

    df_out = pd.DataFrame(rows, columns=['num_timers', 'success_rate', 'mean_runtime'])
    df_out.to_csv(os.path.join('figures', f'{test}-runtime.csv'), mode='w', header=True, index=False, sep=',')
