#!python3
import datetime
import os
import shutil
import statistics
import subprocess

import pandas as pd
import serial
import serial.tools.list_ports

CLOCK_RATE = 240000000
CMAKE_FILE = os.path.join(os.pardir, 'main', 'CMakeLists.txt')
PROJECT_PATH = os.path.abspath(os.pardir)
LOGS_PATH = os.path.join(PROJECT_PATH, 'logs')


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


def gen_comp_flags(test_type: str = 'freertos', task_it=1, num_ticks=1000):
    print("gen new comp flags")
    with open(CMAKE_FILE, "w") as f:
        f.write('idf_component_register(SRCS "main.c" "taskDescriptions.c" INCLUDE_DIRS "." REQUIRES driver esp_psram esp_timer)\n')
        f.write('idf_build_set_property(COMPILE_OPTIONS "-DLOG_LOCAL_LEVEL=ESP_LOG_INFO" APPEND)\n')
        f.write(f'idf_build_set_property(COMPILE_OPTIONS "-DTASK_IT={task_it}" APPEND)\n')
        f.write(f'idf_build_set_property(COMPILE_OPTIONS "-DNUM_TICKS={num_ticks}" APPEND)\n')
        f.write('idf_build_set_property(COMPILE_OPTIONS "-DBENCH_INSERT" APPEND)\n')
        f.write('idf_build_set_property(COMPILE_OPTIONS "-DBENCH_TP_ISR_ALL" APPEND)\n')
        if test_type == 'freertos':
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')
        elif test_type == 'lazytick':
            f.write('idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')
        elif test_type == 'oneshot':
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')
    # print("erasing flash")
    # subprocess.run(['esptool.py', '--chip', 'esp32s3', '--port', device, 'erase_flash'], stdout=subprocess.DEVNULL)
    # subprocess.run(['idf.py', 'fullclean'], cwd=PROJECT_PATH)
    # shutil.rmtree(os.path.join(PROJECT_PATH, 'build'), ignore_errors=True)


def run_eval(period_factor=1, suffix=""):
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # get log
    ser = serial.Serial()
    ser.port = device
    ser.baudrate = 1500000
    ser.timeout = 5
    ser.rts = False
    ser.dtr = False

    ser.open()
    line = ""
    log_raw = []
    while True:
        line = ser.readline().decode(encoding="ISO-8859-1")
        # print(line, end="")
        log_raw.append(line)
        if "RETRIEVAL OUTPUT END" in line:
            break

    # log_raw = [x.decode(encoding="ISO-8859-1") for x in ser.readlines()]
    ser.close()

    LOGFILE = os.path.join(LOGS_PATH, f'{date}{suffix}_log.txt')
    with open(LOGFILE, "w") as f:
        f.writelines(log_raw)

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
        taskset = "harmonic"
    elif not any(log_timer_harmonic):
        taskset = "generic"
    else:
        taskset = "hybrid"
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

    SUMMARY = os.path.join(LOGS_PATH, f'{date}_{taskset}_{log_test_type}{suffix}_eval.txt')

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

    total_runtime_us = log_runtime[2]
    total_runtime = int(total_runtime_us*(10**-6) * CLOCK_RATE)  # cycles
    percent_isr = (total/total_runtime)*100

    with open(SUMMARY, 'w') as o:
        o.write(f"{df.to_string(index=False)}\n")
        o.write(f"{td_df_summary.to_string(index=False)}\n")
        o.write(f"Test type: {log_test_type}\n")
        o.write(f"Taskset: {taskset}\n")
        o.write(f"#Tasks: {log_number_of_tasks}\n")
        o.write(f"#Timers: {log_num_timers}\n")
        o.write(f"#Timers (generic): {num_generic_timers}\n")
        o.write(f"#Timers (harmonic): {num_harmonic_timers}\n")
        o.write(f"total cycles spent in interrupt: {total}\n")
        o.write(f"avg cycles spent in each interrupt: {average}\n")
        o.write(f"Number of Interrupts: {count_isr}\n")
        o.write(f"total runtime: {total_runtime} cycles\n")
        o.write(f'percentage interrupts/total_runtime: {percent_isr}')
    CSV_FILE = os.path.abspath(f'results{suffix}.csv')
    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, "w") as o:
            o.write('test_type,taskset,num_ticks,num_tasks,num_timers,num_generic_timers,num_harmonic_timers,period_factor,total_runtime,count_isr,runtime_isr,avg_isr,percent_isr,insert_counter,insert_mean,insert_median,insert_max,insert_min,insert_span,insert_sum,retrieval_counter,retrieval_mean,retrieval_median,retrieval_max,retrieval_min,retrieval_span,retrieval_sum,deadline_misses\n')
    csv_line = f"{log_test_type},{taskset},{log_num_ticks},{log_number_of_tasks},{log_num_timers},{num_generic_timers},{num_harmonic_timers},{period_factor},{total_runtime},{count_isr},{total},{average},{percent_isr},{insert_counter},{insertion_stats[0]},{insertion_stats[1]},{insertion_stats[2]},{insertion_stats[3]},{insertion_stats[4]},{insertion_stats[5]},{retrieval_counter},{retrieval_stats[0]},{retrieval_stats[1]},{retrieval_stats[2]},{retrieval_stats[3]},{retrieval_stats[4]},{retrieval_stats[5]},{log_deadline_misses}\n"
    with open(CSV_FILE, "+a") as o:
        o.write(csv_line)

    # print(f"insertion stats (mean,median,max,min,max-min): {insertion_stats}")
    # print(f"retrieval stats (mean,median,max,min,max-min): {retrieval_stats}")

    return True


TASK_DESC_C_DEST = os.path.join(PROJECT_PATH, 'main', 'taskDescriptions.c')
TASK_DESC_H_DEST = os.path.join(PROJECT_PATH, 'esp-idf', 'components', 'freertos', 'FreeRTOS-Kernel', 'include', 'freertos', 'taskDescriptions.h')
MIQCP_OUT_DIR = os.path.join(PROJECT_PATH, 'miqcp')


def copytds(tasksettype, pf, num_timer, num_tasks):
    td_dir = os.path.join(MIQCP_OUT_DIR, f'td-{tasksettype}')
    shutil.copy(src=os.path.join(td_dir, f'taskDescriptions-t{num_tasks}-tim{num_timer}-p{pf}.h'), dst=TASK_DESC_H_DEST)
    shutil.copy(src=os.path.join(td_dir, f'taskDescriptions-t{num_tasks}-tim{num_timer}-p{pf}.c'), dst=TASK_DESC_C_DEST)


def run_test(tasksettype, test_type, tasks, timers):
    pf = 1
    copytds(tasksettype, pf=pf, num_timer=timers, num_tasks=tasks)
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} running rebuild')
    # subprocess.run(['./rebuild.sh'], cwd=os.path.join(PROJECT_PATH, 'scripts'), shell=True)
    os.system('./rebuild.sh')
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} t{tasks}-tim{timers}-p{pf}: running {test_type} with {tasksettype} taskset')
    success = False
    while not success:
        try:
            success = run_eval(period_factor=pf, suffix="")
        except Exception as e:
            print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} ERROR, trying again')
            print(e)
            os.system('./reset.sh')
            os.system('./rebuild.sh')
            pass


if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)
device = [port for port, desc, hwid in serial.tools.list_ports.comports() if port.startswith("/dev/cu.usbmodem") or port == "/dev/ttyACM0"][0]


for tim in range(1, 5):
    for tasks in range(50, 550, 50):
        for taskset in ['harmonic', 'generic', 'hybrid']:
            for test in ['freertos', 'lazytick', 'oneshot']:
                # 1000 ticks with 1tick=10ms => 10s tests
                gen_comp_flags(test_type=test, task_it=1, num_ticks=1000)
                run_test(tasksettype=taskset, test_type=test, tasks=tasks, timers=tim)
