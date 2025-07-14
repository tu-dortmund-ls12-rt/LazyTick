#!/bin/bash
LOG_FOLDER=../logs
ESP_IDF=../esp-idf
DATE=$(date +"%Y-%m-%dT%H:%M:%S%z")
mkdir -p $LOG_FOLDER/logs-generic
mkdir -p $LOG_FOLDER/logs-harmonic
mkdir -p $LOG_FOLDER/logs-hybrid

. $ESP_IDF/export.sh

p=1
t=5
# for t in {1..5}
# do
for i in {50..500..50}
do
python3 miqcp-eval-generic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-generic/$DATE-t${i}-tim${t}-p${p}_log.txt
python3 miqcp-eval-harmonic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-harmonic/$DATE-t${i}-tim${t}-p${p}_log.txt
python3 miqcp-eval-hybrid.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-hybrid/$DATE-t${i}-tim${t}-p${p}_log.txt
done
# done