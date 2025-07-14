import pandas as pd

NUM_TESTS = 99  # number of tests per timer count

files = [
    'harmonic',
    'generic']

for file in files:
    df = pd.read_csv(f'miqcp-eval-{file}.csv', sep=';')
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
    df_out.to_csv(f'{file}-runtime.csv', mode='w', header=True, index=False, sep=',')
