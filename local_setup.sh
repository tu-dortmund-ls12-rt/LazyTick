#!/bin/sh

thispath=$(realpath .)

git clone -b v5.3.1 --recursive https://github.com/espressif/esp-idf.git

cd $thispath/esp-idf
chmod +x install.sh
./install.sh esp32s3
. ./export.sh

# install python packages in idf virtual environment
pip install pandas numpy gurobipy pyserial jinja2

# setup lazytick kernel modification files
rm -rf $thispath/esp-idf/components/freertos && \
ln -s $thispath/src/freertos $thispath/esp-idf/components/freertos

rm $thispath/esp-idf/components/xtensa/xtensa_vectors.S && \
ln -s $thispath/src/xtensa_vectors.S $thispath/esp-idf/components/xtensa/xtensa_vectors.S

rm $thispath/esp-idf/components/esp_hw_support/intr_alloc.c && \
ln -s $thispath/src/intr_alloc.c $thispath/esp-idf/components/esp_hw_support/intr_alloc.c

rm $thispath/esp-idf/components/pthread/pthread.c && \
ln -s $thispath/src/pthread.c $thispath/esp-idf/components/pthread/pthread.c

rm $thispath/esp-idf/components/esp_timer/src/esp_timer.c && \
ln -s $thispath/src/esp_timer.c $thispath/esp-idf/components/esp_timer/src/esp_timer.c