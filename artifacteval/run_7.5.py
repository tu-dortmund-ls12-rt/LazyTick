#!python3
import datetime
import os
import shutil

import serial
import serial.tools.list_ports

CMAKE_FILE = os.path.join(os.pardir, 'main', 'CMakeLists.txt')
PROJECT_PATH = os.path.abspath(os.pardir)

LOGS_PATH = os.path.join(PROJECT_PATH, 'logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))


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


def run_eval(suffix=""):
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # get log
    ser = serial.Serial()
    ser.port = device
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
        if "RETRIEVAL OUTPUT END" in line:
            break
        if 'abort: deadline miss' in line:
            return True  # skip when deadline miss occurs

    # log_raw = [x.decode(encoding="ISO-8859-1") for x in ser.readlines()]
    ser.close()

    LOGFILE = os.path.join(LOGS_PATH, f'{date}{suffix}.log')
    with open(LOGFILE, "w") as f:
        f.writelines(log_raw)
    return True


TASK_DESC_C_DEST = os.path.join(PROJECT_PATH, 'main', 'taskDescriptions.c')
TASK_DESC_H_DEST = os.path.join(PROJECT_PATH, 'esp-idf', 'components', 'freertos', 'FreeRTOS-Kernel', 'include', 'freertos', 'taskDescriptions.h')
MIQCP_OUT_DIR = os.path.abspath('helperscripts')


def copytds(tasksettype, pf, num_timer, num_tasks):
    td_dir = os.path.join(MIQCP_OUT_DIR, f'td-{tasksettype}')
    shutil.copy(src=os.path.join(td_dir, f'taskDescriptions-t{num_tasks}-tim{num_timer}-p{pf}.h'), dst=TASK_DESC_H_DEST)
    shutil.copy(src=os.path.join(td_dir, f'taskDescriptions-t{num_tasks}-tim{num_timer}-p{pf}.c'), dst=TASK_DESC_C_DEST)


def run_test(tasksettype, test_type, tasks, timers):
    pf = 1
    copytds(tasksettype, pf=pf, num_timer=timers, num_tasks=tasks)
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} running rebuild')
    os.system('./rebuild.sh')
    print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} t{tasks}-tim{timers}-p{pf}: running {test_type} with {tasksettype} taskset')
    success = False
    while not success:
        try:
            success = run_eval(suffix=f'_{test_type}_{tasksettype}-t{tasks}-tim{timers}-p{pf}')
        except Exception as e:
            print(f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")} ERROR, trying again')
            print(e)
            os.system('./reset.sh')
            os.system('./rebuild.sh')
            pass


if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)
device = [port for port, desc, hwid in serial.tools.list_ports.comports() if port.startswith("/dev/cu.usbmodem") or port == "/dev/ttyACM0"][0]


for test in ['lazytick', 'oneshot', 'freertos']:
    for taskset in ['harmonic', 'generic']:
        for tim in [1, 2, 3, 4]:
            for tasks in range(50, 550, 50):
                # 1000 ticks with 1tick=100ms => 100s per test
                gen_comp_flags(test_type=test, task_it=1, num_ticks=1000)
                run_test(tasksettype=taskset, test_type=test, tasks=tasks, timers=tim)
