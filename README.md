# LazyTick EMSOFT 2025 Artifact Evaluation
This branch contains the code for reproducing the results our EMSOFT 2025 submission LazyTick.

## How to use the artifact
To use the artifact and reproduce the evaluation results, the following steps have to be executed:
1. download the artifact evaluation release from: ``
2. install all software dependencies listed in the requirements section
3. run the `local_setup.sh` script to install the esp-idf and apply the kernel modifications of LazyTick
4. run the `run_all.sh` script in the `artifacteval` folder
5. after all experiments have finished, the figures with the replicated results can be found in `artifacteval/figures`. Each figure corresponds to the figure in the section of the same name.

## Requirements
The following software and hardware requirements need to be met in order to replicate the evaluation results.

### Software Environment
The following software environment is required to run the code of this artifact:
- Linux host (tested with Debian 12.11 x86)
- Packages needed for esp-idf (https://docs.espressif.com/projects/esp-idf/en/v5.3.1/esp32/get-started/linux-macos-setup.html#for-linux-users):
    git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
- python3 (tested with python 3.11.2)
- Gurobi license to solve the MIQCP
- LaTeX to generate the figures from the csv data

### Required Hardware
The following hardware is required to replicate the results:
- ESP32-S3-DevKitC-1-N32R8V
- High-performance server to replicate the MIQCP runtime results (we used a server with 2 AMD EPYC 9654 CPUs and 768GB of RAM in our evaluation)

### Notes on MIQCP runtime experiments
The runtime results of the MIQCP experiments are dependant on the hardware where gurobi runs on.
The task sets with with 1-4 timers can be solved in little time even on a desktop class computer. In order to replicate the results for 5-8 timers, a high-performance server system is needed.
For this reason, we have configured the script to only solve the MIQCP instances for 1-4 timers. However, this is configurable in the script `artifacteval/helperscripts/solve_task_sets.sh`. The range of timers for which the MIQCP instances are solved can be configured with the loop bounds in line 2.


## Install
Whether the software and hardware environment is correctly setup can be check by running:
1. `. ./esp-idf/export.sh` from the root of the repository to activate the `idf.py` commands.
2. `idf.py build flash` to build and flash the firmware to the ESP32.
3. `idf.py monitor` to display the UART output of the experiment run.
4. When an experiment run has finished without errors, the last displayed line should look like: `I output_retr: RETRIEVAL OUTPUT END` when running experiments for figures 7.5, 7.6, 7.7 or `I output: INTERRUPT OUTPUT END` when running the deadline miss experiments for figure 7.8.