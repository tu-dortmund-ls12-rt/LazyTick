#!/bin/bash
thispath=$(realpath .)

cd $thispath/helperscripts
for t in {1..4}
do
# small tests
for i in {10..50..5}
do
echo $i
python3 solve_generic.py --tasks $i --timers $t
python3 solve_harmonic.py --tasks $i --timers $t
done
# large tests
for j in {50..500..50}
do
python3 solve_generic.py --tasks $j --timers $t
python3 solve_harmonic.py --tasks $j --timers $t
done
done
python3 solve_waters.py