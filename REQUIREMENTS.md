## Requirements
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