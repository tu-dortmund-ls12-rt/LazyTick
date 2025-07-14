#!/bin/bash
cd ..
. ./esp-idf/export.sh
idf.py fullclean
rm -rf build
idf.py build
idf.py flash -p /dev/ttyACM0