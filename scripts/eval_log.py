#!python3
import argparse
import os
import statistics
from typing import List

import pandas as pd

CLOCK_RATE = 240000000


def extract(string, key, current_var, is_list, type=int):
    if key in string:
        value = string.split(f"{key}=")[1]
        if is_list:
            if type == bool:
                return [x == 'True' for x in value.split(',')]
            else:
                return [type(x) for x in value.split(',')]
        elif type == str:
            return str(value)
        else:
            return int(value)
    else:
        return current_var if current_var != -1 else -1


def evaluate_log(log_raw: List, taskset_type: str, suffix: str = ""):
    # process log
    log = [s.strip() for s in log_raw]
    # get STX and EOT symbols
    stx = eot = -1
    ins_start = ins_end = -1
    ret_start = ret_end = -1
    for i, l in enumerate(log):
        if "INTERRUPT OUTPUT START" in l:
            stx = i
        if "INTERRUPT OUTPUT END" in l:
            eot = i
        if "INSERT OUTPUT START" in l:
            ins_start = i
        if "INSERT OUTPUT END" in l:
            ins_end = i
        if "RETRIEVAL OUTPUT START" in l:
            ret_start = i
        if "RETRIEVAL OUTPUT END" in l:
            ret_end = i
    results = log[stx+1:eot-1]
    results_ins = log[ins_start+1:ins_end-1]
    results_ret = log[ret_start+1:ret_end-1]
    if stx == -1 or eot == -1:
        raise Exception("no start or end symbol found in output")

    log_test_type = log_period_factor = log_number_of_tasks = log_num_timers = log_timer_periods = log_timer_harmonic = log_runtime = log_deadline_misses = log_num_ticks = -1

    for s in log:
        log_test_type = extract(s, 'test_type', log_test_type, False, str)
        log_period_factor = extract(s, 'period_factor', log_period_factor, False, int)
        log_number_of_tasks = extract(s, 'number_of_tasks', log_number_of_tasks, False, int)
        log_num_timers = extract(s, 'number_of_timers', log_num_timers, False, int)
        log_num_ticks = extract(s, 'num_ticks', log_num_ticks, False, int)
        log_timer_periods = extract(s, 'timer_periods', log_timer_periods, True, int)
        log_timer_harmonic = extract(s, 'timer_harmonic', log_timer_harmonic, True, bool)
        log_runtime = extract(s, 'time_us(start_tp,end_tp,duration)', log_runtime, True, int)
        log_deadline_misses = extract(s, 'deadline_misses', log_deadline_misses, False, int)
    stats = [log_test_type, log_period_factor, log_number_of_tasks, log_num_timers, log_timer_periods, log_timer_harmonic, log_runtime, log_deadline_misses, log_num_ticks]
    if any([s == -1 for s in stats]):
        raise Exception(f"not all stats collected: {stats}")
    # print(stats)

    # print(results_ins)
    insertion_times = [int(t.split(',')[1]) for t in results_ins]
    insertion_stats = (statistics.mean(insertion_times), statistics.median(insertion_times), max(insertion_times), min(insertion_times), max(insertion_times)-min(insertion_times), sum(insertion_times))
    # print(results_ret)
    retrieval_times = [int(t.split(',')[1]) for t in results_ret]
    retrieval_stats = (statistics.mean(retrieval_times), statistics.median(retrieval_times), max(retrieval_times), min(retrieval_times), max(retrieval_times)-min(retrieval_times), sum(retrieval_times))

    insert_counter = len(insertion_times)
    retrieval_counter = len(retrieval_times)

    if all(log_timer_harmonic):
        effective_taskset = "harmonic"
    elif not any(log_timer_harmonic):
        effective_taskset = "generic"
    else:
        effective_taskset = "hybrid"
    num_harmonic_timers = sum(log_timer_harmonic)
    num_generic_timers = log_num_timers - num_harmonic_timers

    # extract task description
    task_desc_start = next(i for i, l in enumerate(log) if "Start Task Description" in l)
    task_desc_end = next(i for i, l in enumerate(log) if "End Task Description" in l)

    task_desc = log[task_desc_start+1:task_desc_end]

    task_desc_arr = []
    for t in task_desc:
        comp = t.split(";")[1].strip().split(',')
        task_name = comp[0]
        period = int(comp[1])
        timer = int(comp[2])
        task_desc_arr.append({"timer": timer, "period": period})

    td_df = pd.DataFrame.from_dict(task_desc_arr)
    pd.options.display.max_columns = len(td_df.columns)
    pd.options.display.max_rows = len(td_df)

    td_df_summary = td_df.groupby("period").size().reset_index(name='counts')

    # SUMMARY = os.path.join(LOGS_PATH, f'{date}_{taskset}_{log_test_type}{suffix}_eval.txt')

    d = []
    for l in results:
        components = l.split(',')
        taskname = components[2]
        it = int(components[0].split(':')[1].strip())
        ccycles = int(components[1])
        marker = components[3]
        d.append({"interrupt": it, "ccycle": ccycles, "marker": f"{taskname}: {marker}"})

    # sanity check
    for i in range(1, len(d), 2):
        it_pre = d[i-1]["interrupt"]
        it_post = d[i]["interrupt"]
        marker_pre = int(d[i-1]["marker"].split(" ")[1])
        marker_post = int(d[i]["marker"].split(" ")[1])
        if it_post != it_pre+1:
            raise ValueError("interrupts not contiguous")
        if marker_pre == marker_post-1:
            continue
        else:
            raise ValueError(
                f"Markers: {(marker_pre, marker_post)} for Interrupt: {(it_pre, it_post)} do not match correctly")

    df = pd.DataFrame.from_dict(d)
    pd.options.display.max_columns = len(df.columns)
    pd.options.display.max_rows = len(df)

    # calculate total
    d2 = []
    for i in range(1, len(d), 2):
        it_start = int(d[i-1]["interrupt"])
        it_end = int(d[i]["interrupt"])
        start = int(d[i-1]["ccycle"])
        end = int(d[i]["ccycle"])
        marker_start = d[i-1]["marker"]
        marker_end = d[i]["marker"]
        d2.append({"interrupts": f"{it_start} -> {it_end}", "marker pre": f"{marker_start}", "marker post": f"{marker_end}", "runtime": (end-start), "ccycle start": start, "ccycle end": end})

    df = pd.DataFrame.from_dict(d2)

    pd.options.display.max_columns = len(df.columns)
    pd.options.display.max_rows = len(df)

    total = df['runtime'].sum()
    average = df['runtime'].mean()
    count_isr = df['runtime'].count()
    isr_max = df['runtime'].max()
    isr_min = df['runtime'].min()
    isr_span = isr_max-isr_min

    combined_overhead = insertion_stats[5] + total # insert sum + isr sum

    total_runtime_us = log_runtime[2]
    total_runtime = int(total_runtime_us*(10**-6) * CLOCK_RATE)  # cycles
    percent_isr = (total/total_runtime)*100

    # with open(SUMMARY, 'w') as o:
    #     o.write(f"{df.to_string(index=False)}\n")
    #     o.write(f"{td_df_summary.to_string(index=False)}\n")
    #     o.write(f"Test type: {log_test_type}\n")
    #     o.write(f"Taskset: {taskset}\n")
    #     o.write(f"#Tasks: {log_number_of_tasks}\n")
    #     o.write(f"#Timers: {log_num_timers}\n")
    #     o.write(f"#Timers (generic): {num_generic_timers}\n")
    #     o.write(f"#Timers (harmonic): {num_harmonic_timers}\n")
    #     o.write(f"total cycles spent in interrupt: {total}\n")
    #     o.write(f"avg cycles spent in each interrupt: {average}\n")
    #     o.write(f"Number of Interrupts: {count_isr}\n")
    #     o.write(f"total runtime: {total_runtime} cycles\n")
    #     o.write(f'percentage interrupts/total_runtime: {percent_isr}')
    csv_line = f"{log_test_type},{taskset_type},{effective_taskset},{log_num_ticks},{log_number_of_tasks},{log_num_timers},{num_generic_timers},{num_harmonic_timers},{total_runtime},{count_isr},{total},{average},{percent_isr},{isr_max},{isr_min},{isr_span},{insert_counter},{insertion_stats[0]},{insertion_stats[1]},{insertion_stats[2]},{insertion_stats[3]},{insertion_stats[4]},{insertion_stats[5]},{retrieval_counter},{retrieval_stats[0]},{retrieval_stats[1]},{retrieval_stats[2]},{retrieval_stats[3]},{retrieval_stats[4]},{retrieval_stats[5]},{combined_overhead},{log_deadline_misses}\n"
    with open(CSV_FILE, "+a") as o:
        o.write(csv_line)

    # print(f"insertion stats (mean,median,max,min,max-min): {insertion_stats}")
    # print(f"retrieval stats (mean,median,max,min,max-min): {retrieval_stats}")


parser = argparse.ArgumentParser(description="Parse directory")
parser.add_argument("--dir", type=str, required=True)
args = parser.parse_args()

directory = os.path.abspath(args.dir)

CSV_FILE = os.path.abspath(f'results.csv')
if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, "w") as o:
        o.write('test_type,taskset,effective_taskset,num_ticks,num_tasks,num_timers,num_generic_timers,num_harmonic_timers,total_runtime,count_isr,runtime_isr,avg_isr,percent_isr,isr_max,isr_min,isr_span,insert_counter,insert_mean,insert_median,insert_max,insert_min,insert_span,insert_sum,retrieval_counter,retrieval_mean,retrieval_median,retrieval_max,retrieval_min,retrieval_span,retrieval_sum,combined_overhead,deadline_misses\n')

for file in sorted(os.listdir(directory)):
    filename = os.fsdecode(file)
    if filename.endswith(".log"):
        with open(os.path.join(directory, filename), 'r') as f:
            taskset = filename.split('_')[2].split('-')[0]
            log_raw = f.readlines()
            evaluate_log(log_raw, taskset_type=taskset)
