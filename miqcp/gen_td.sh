#!/bin/bash
LOG_FOLDER=../logs
ESP_IDF=../esp-idf
DATE=$(date +"%Y-%m-%dT%H:%M:%S%z")
mkdir -p $LOG_FOLDER/logs-generic
mkdir -p $LOG_FOLDER/logs-harmonic
mkdir -p $LOG_FOLDER/logs-waters

. $ESP_IDF/export.sh

p=1
for t in {1..4}
do
# small tests
for i in {10..50..5}
do
python3 miqcp-eval-generic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-generic/$DATE-t${i}-tim${t}-p${p}_log.txt
python3 miqcp-eval-harmonic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-harmonic/$DATE-t${i}-tim${t}-p${p}_log.txt
done
# large tests
for i in {50..500..50}
do
python3 miqcp-eval-generic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-generic/$DATE-t${i}-tim${t}-p${p}_log.txt
python3 miqcp-eval-harmonic.py --tasks $i --timers $t --period_factor $p | tee $LOG_FOLDER/logs-harmonic/$DATE-t${i}-tim${t}-p${p}_log.txt
done
done
python3 waters.py | tee $LOG_FOLDER/logs-waters/$DATE-t${i}-tim${t}-p${p}_log.txt