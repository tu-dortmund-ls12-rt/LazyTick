import datetime
import os
import shutil
import subprocess

import serial
import pandas as pd

CMAKE_FILE = os.path.join(os.pardir, 'main', 'CMakeLists.txt')
PROJECT_PATH = os.path.abspath(os.pardir)
DEVICE = "/dev/ttyACM0"
LOGS_PATH = os.path.join('figures', 'results-deadline', 'logs')
CSV_FILE = os.path.join('figures', 'results-deadline','results.csv')

TABLE_TEMPLATE = r"""
\begin{table}
    \centering
    \begin{tabular}{l<{\hspace{.25cm}}llll}
        \toprule
        {CONTENT}             
        \bottomrule
    \end{tabular}
    \vspace*{1ex}%
    \caption{Number of tasks that can be executed without deadline misses.}\label{table:deadlinemiss}
\end{table}
"""

def gen_comp_flags(test_type: str = 'freertos', num_ticks=1000):
    print("gen new comp flags")
    with open(CMAKE_FILE, "w") as f:
        f.write('idf_component_register(SRCS "main.c" "taskDescriptions.c" INCLUDE_DIRS "." REQUIRES driver esp_psram esp_timer)\n')
        f.write('idf_build_set_property(COMPILE_OPTIONS "-DLOG_LOCAL_LEVEL=ESP_LOG_INFO" APPEND)\n')
        f.write(f'idf_build_set_property(COMPILE_OPTIONS "-DTASK_IT=1" APPEND)\n')
        f.write(f'idf_build_set_property(COMPILE_OPTIONS "-DNUM_TICKS={num_ticks}" APPEND)\n')
        f.write('idf_build_set_property(COMPILE_OPTIONS "-DDEADLINE_TEST=1" APPEND)\n')
        if test_type == 'freertos':
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')
        elif test_type == 'lazytick':
            f.write('idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')
        elif test_type == 'oneshot':
            f.write('# idf_build_set_property(COMPILE_OPTIONS "-DSYSTICK_DISABLED" APPEND)\n')
            f.write('idf_build_set_property(COMPILE_OPTIONS "-DONESHOT" APPEND)\n')


def run_eval(suffix=""):
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    success = False

    # get log
    ser = serial.Serial()
    ser.port = DEVICE
    ser.baudrate = 1500000
    ser.timeout = 120
    ser.rts = False
    ser.dtr = False

    ser.open()
    line = ""
    log_raw = []
    while True:
        line = ser.readline().decode(encoding="ISO-8859-1")
        log_raw.append(line)
        if "INTERRUPT OUTPUT END" in line:
            success = True
            break
        if 'abort deadline miss' in line:
            break  # skip when deadline miss occurs

    ser.close()

    LOGFILE = os.path.join(LOGS_PATH, f'{date}{suffix}.log')
    with open(LOGFILE, "w") as f:
        f.writelines(log_raw)
    return success


TASK_DESC_C_DEST = os.path.join(PROJECT_PATH, 'main', 'taskDescriptions.c')
TASK_DESC_H_DEST = os.path.join(PROJECT_PATH, 'esp-idf', 'components', 'freertos', 'FreeRTOS-Kernel', 'include', 'freertos', 'taskDescriptions.h')
MIQCP_OUT_DIR = os.path.join(PROJECT_PATH, 'miqcp')

TD_C = '''
#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {{pdTRUE}};
const TickType_t timerPeriods[1] = {{number_of_tasks}};
const TaskDescriptor_t td[number_of_tasks] = {{{tds}}};
'''

TD_H = '''
#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {{
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
    TickType_t executionTime;
}} TaskDescriptor_t;

#define tick(i) (i*159999U)

#define number_of_timers 1
#define number_of_tasks {num_tasks}
#define HYPERPERIOD (2*number_of_tasks)
#define NUM_INTERRUPTS 60
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL number_of_tasks
extern const BaseType_t is_harmonic_timer[1];
extern const TickType_t timerPeriods[1];
extern const TaskDescriptor_t td[number_of_tasks];
#endif
'''


def copytds(num_tasks):
    with open(TASK_DESC_H_DEST, 'w') as f:
        f.write(TD_H.format(num_tasks=num_tasks).strip())
    # generate td set
    tds = [f'{{0,number_of_tasks,{i},tick(1)}}' for i in range(0, num_tasks-1)]
    tds.append(f'{{0,2*number_of_tasks,{num_tasks-1},tick(2)-1500}}')
    with open(TASK_DESC_C_DEST, 'w') as f:
        f.write(TD_C.format(tds=','.join(tds)).strip())

def rebuild():
    cmd = (
        ". ./esp-idf/export.sh && "
        "idf.py fullclean && "
        "rm -rf build && "
        "idf.py build && "
        f"idf.py flash -p {DEVICE}"
    )
    subprocess.run(cmd, shell=True, cwd=PROJECT_PATH, check=True)


def reset():
    cmd = (
        ". ./esp-idf/export.sh && "
        f"esptool.py --chip esp32s3 --port {DEVICE} erase_flash"
    )
    subprocess.run(cmd, shell=True, cwd=PROJECT_PATH, check=True)

def run_test(test_type, tasks, timers):
    copytds(num_tasks=tasks)
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} running rebuild')
    rebuild()
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} t{tasks}-tim{timers}: running {test_type}')
    success = run_eval(suffix=f'_{test_type}-t{tasks}-tim{timers}')
    with open(CSV_FILE, 'a') as f:
        f.write(f'{test_type},{timers},{tasks},{success}\n')


# def set_freertos_hz(tick: int):
#     sdkconfig = os.path.join(PROJECT_PATH, 'sdkconfig')
#     with open(sdkconfig, 'r') as file:
#         lines = file.readlines()
#     for i, line in enumerate(lines):
#         if line.startswith('CONFIG_FREERTOS_HZ='):
#             lines[i] = f'CONFIG_FREERTOS_HZ={tick}\n'
#             break
#     with open(sdkconfig, 'w') as file:
#         file.writelines(lines)


# def enable_compiler_opt(opt: bool):
#     sdkconfig = os.path.join(PROJECT_PATH, 'sdkconfig')
#     with open(sdkconfig, 'r') as file:
#         lines = file.readlines()
#     for i, line in enumerate(lines):
#         if opt:
#             if line.startswith('CONFIG_COMPILER_OPTIMIZATION_PERF='):
#                 lines[i] = 'CONFIG_COMPILER_OPTIMIZATION_PERF=y\n'
#             if line.startswith('CONFIG_COMPILER_OPTIMIZATION_NONE='):
#                 lines[i] = '# CONFIG_COMPILER_OPTIMIZATION_NONE is not set\n'
#         else:
#             if line.startswith('CONFIG_COMPILER_OPTIMIZATION_PERF='):
#                 lines[i] = '# CONFIG_COMPILER_OPTIMIZATION_PERF is not set\n'
#             if line.startswith('CONFIG_COMPILER_OPTIMIZATION_NONE='):
#                 lines[i] = 'CONFIG_COMPILER_OPTIMIZATION_NONE=y\n'

#     with open(sdkconfig, 'w') as file:
#         file.writelines(lines)


os.makedirs(LOGS_PATH, exist_ok=True)

if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, 'w') as f:
        f.write('testtype,timers,tasks,schedulable\n')

sdkconfig = os.path.join(PROJECT_PATH, 'sdkconfig.7.8')
shutil.copy(sdkconfig, os.path.join(PROJECT_PATH, 'sdkconfig'))

# config should be -O2, 10ms tick, and BENCH_INSERT, BENCH_TP_ISR_ALL disabled
for test in ['lazytick', 'oneshot', 'freertos']:
    for tim in [1]:
        for tasks in range(2, 21):
            gen_comp_flags(test_type=test, num_ticks=1000)
            run_test(test_type=test, tasks=tasks, timers=tim)

# parse results
df = pd.read_csv(CSV_FILE)
max_schedulable = df[df['schedulable'] == True].groupby('testtype')['tasks'].max().astype(int)
latex_table = max_schedulable.reset_index().pivot_table(index=None, columns='testtype', values='tasks')
latex_table = latex_table.astype(int).map(lambda x: f"{x} tasks")
out = latex_table.to_latex(index=False, header=True, column_format='l' * (len(latex_table.columns)))
out = "\n".join(out.splitlines()[2:-2])

tex = TABLE_TEMPLATE.replace('{CONTENT}', out)
with open(os.path.join('figures', '7.8-table.tex'), 'w') as f:
    f.write(tex)