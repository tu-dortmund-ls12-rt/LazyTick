#!/bin/sh

thispath=$(realpath .)

git clone -b v5.3.1 --recursive https://github.com/espressif/esp-idf.git

cd $thispath/esp-idf
chmod +x install.sh
./install.sh esp32s3
. ./export.sh

cp -r $thispath/esp-idf/components/freertos $thispath/src/freertos && \
rm -rf $thispath/esp-idf/components/freertos && \
ln -s $thispath/src/freertos $thispath/esp-idf/components/freertos

cp $thispath/esp-idf/components/xtensa/xtensa_vectors.S $thispath/src/xtensa_vectors.S && \
rm $thispath/esp-idf/components/xtensa/xtensa_vectors.S && \
ln -s $thispath/src/xtensa_vectors.S $thispath/esp-idf/components/xtensa/xtensa_vectors.S

cp $thispath/esp-idf/components/esp_hw_support/intr_alloc.c $thispath/src/intr_alloc.c && \
rm $thispath/esp-idf/components/esp_hw_support/intr_alloc.c && \
ln -s $thispath/src/intr_alloc.c $thispath/esp-idf/components/esp_hw_support/intr_alloc.c

cp $thispath/esp-idf/components/pthread/pthread.c $thispath/src/pthread.c && \
rm $thispath/esp-idf/components/pthread/pthread.c && \
ln -s $thispath/src/pthread.c $thispath/esp-idf/components/pthread/pthread.c

cp $thispath/esp-idf/components/esp_timer/src/esp_timer.c $thispath/src/esp_timer.c && \
rm $thispath/esp-idf/components/esp_timer/src/esp_timer.c && \
ln -s $thispath/src/esp_timer.c $thispath/esp-idf/components/esp_timer/src/esp_timer.c