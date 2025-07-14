#!/bin/bash
cd ..
. ./esp-idf/export.sh
esptool.py --chip esp32s3 --port /dev/ttyACM0 erase_flash