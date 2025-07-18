#!/bin/bash
. ../esp-idf/export.sh
python3 run_7.4.py
python3 run_7.5.py
python3 run_7.6.py
# python3 run_7.7.py
python3 run_7.8.py
python3 run_7.9.py
cd figures
bash -c "./compile_all.sh"