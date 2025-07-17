#!/bin/bash
for t in {1..4}
do
# small+large+miqcp runtime tests
for i in {5..500..5}
do
echo $i
python3 solve_generic.py --tasks $i --timers $t
python3 solve_harmonic.py --tasks $i --timers $t
done
done
python3 solve_waters.py