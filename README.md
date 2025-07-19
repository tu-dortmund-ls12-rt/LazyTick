# LazyTick EMSOFT 2025 Artifact Evaluation

This repository is used to reproduce the evaluation results from our EMSOFT 2025 submission

_LazyTick: Lazy and Efficient Management of Job Release in Real-Time Operating Systems_

for artifact evaluation. This document explains how to use the artifact to repeat the experiments presented in the paper, i.e., Section 7. Please cite the above paper when reporting, reproducing or extending the results.
We tested the artifact with a clean Debian 12.11 x86 host with an Intel Core i3-10305T CPU and 8 GB of RAM.

The rest of the document is organized as follows:
1. [Environment Setup](#environment-setup)
2. [How to deploy](#how-to-deploy)
3. [How to run the experiments](#how-to-run-the-experiments)
4. [Overview of the corresponding functions](#overview-of-the-corresponding-functions)
4. [Miscellaneous](#miscellaneous)

## Environment Setup
The following software and hardware requirements need to be met in order to replicate the evaluation results.

### Software Environment

The [required software packages](https://docs.espressif.com/projects/esp-idf/en/v5.3.1/esp32/get-started/linux-macos-setup.html#for-linux-users) to use the esp-idf have to be installed, e.g. for Debian 12:
```
git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```
To solve the MIQCP instances, a license for Gurobi is needed.
To run the scripts of the evaluation Python 3.11 was used.
In addition to the Python environment provided by the esp-idf, the following Python packages and versions are used:
```sh
pandas==2.3.1 numpy==2.3.1 gurobipy==12.0.3 pyserial==3.5 Jinja2==3.1.6
```
The figures are created with LaTeX. The generation of the figures was tested with the LaTeX distribution provided by the
```sh
texlive-full
```
package.

### Required Hardware
The following hardware is required to replicate the results:
- ESP32-S3-DevKitC-1-N32R8V
- High-performance server to replicate the MIQCP runtime results (we used a server with 2 AMD EPYC 9654 CPUs and 768 GB of RAM in our evaluation)

## File Structure
All evaluation files regarding the artifact evaluation are found in the artifacteval folder.

    .
    ├── artifacteval            # Artifact evaluation files
    │   ├── figures             # The generated figures from the evaluation data
    │       └── compile_all.sh  # Script compile all LaTeX figures
    │   ├── helperscripts       # Folder containing scripts for the MIQCP
    │       └── pregenerated    # Pre-solved task sets
    │   └── run_all.sh          # Script to run all experiments
    ├── esp-idf                 # ESP-IDF installation after running the setup script
    ├── src                     # ESP-IDF FreeRTOS Kernel modifications from LazyTick
    ├── INSTALL.md              # How to check the installation
    ├── REQUIREMENTS.md         # Details from the requirements section
    ├── STATUS.md               # Which badges we apply for
    └── README.md               # This document

## How to deploy

1. Clone the git repository or download the [zip file](https://github.com/tu-dortmund-ls12-rt/LazyTick/archive/refs/heads/artifacteval.zip):
    ```
    https://github.com/tu-dortmund-ls12-rt/LazyTick.git
    ```
    and switch to the `artifacteval` branch:
    ```sh
    git checkout artifacteval
    ```

2. Run the `local_setup.sh` script to install the esp-idf and apply the kernel modifications of LazyTick.
3. Run the `run_all.sh` script in the `artifacteval` folder to run the experiments. A full run takes around 18 hours on our system.
4. After all experiments have finished, the figures with the replicated results can be found in `artifacteval/figures`. Each figure corresponds to the figure in the section of the same name.

## How to run the experiments

All experiments can be run by executing the script `run_all.sh` from the `artifacteval`.
Alternatively, the following Section describes how to run experiments for each evaluation figure separately.

### Running experiments for each section separately
The experiments for each section can be run separately by executing the corresponding python scripts in the `artifacteval` folder.

In order to build the firmware for each experiment run, the task set obtained by solving MIQCP instance needs to exist in the folder `artifacteval/helperscripts`.
To obtain the task sets, the MIQCP instances can be solved by running the script `artifacteval/helperscripts/solve_task_sets.sh`. A Gurobi license is required for this.
Alternatively, pre-solved task sets for 1-4 timers are available in the folder `artifacteval/helperscripts/pregenerated`. To use these instead of generating task sets from scratch, copy the contents of the folder to `artifacteval/helperscripts/`, e.g., run `cp -r artifacteval/helperscripts/pregenerated/* artifacteval/helperscripts/` from the root of the repository.

As long as the data for the corresponding figure has been collected, each figure can be separately created by compiling the corresponding `.tex` file in the `artifacteval/figures` folder.

## Miscellaneous
The following Sections give some notes on the MIQCP runtime experiments and how to check if the esp-idf installation was successful.

### Notes on MIQCP runtime experiments
The runtime results of the MIQCP experiments are dependent on the hardware where Gurobi runs on.
The task sets with 1-4 timers can be solved in little time even on a desktop class computer. In order to replicate the results for 5-8 timers, a high-performance server system is needed.
For this reason, we have configured the script to only solve the MIQCP instances for 1-4 timers. However, this is configurable in the script `artifacteval/helperscripts/solve_task_sets.sh`. The range of timers for which the MIQCP instances are solved can be configured with the loop bounds in line 2.


### Install
Whether the software and hardware environment is correctly set up can be checked by running:
1. `. ./esp-idf/export.sh` from the root of the repository to activate the `idf.py` commands.
2. `idf.py build flash` to build and flash the firmware to the ESP32.
3. `idf.py monitor` to display the UART output of the experiment run.
4. When an experiment run has finished without errors, the last displayed line should look like: `I output_retr: RETRIEVAL OUTPUT END` when running experiments for figures 7.5, 7.6, 7.7 or `I output: INTERRUPT OUTPUT END` when running the deadline miss experiments for figure 7.8.