from collections import defaultdict

from numpy import lcm

TIMERS = [9,5,7,6]

TASKS = [2, 4, 6, 16]

# HYPERPERIOD = int(lcm.reduce([2, 4, 6, 16]))
HYPERPERIOD = 101
# HYPERPERIOD = 200

interrupts = defaultdict(list)

for i in range(1, HYPERPERIOD):
    for t in sorted(TIMERS):
        if i % t == 0:
            interrupts[i].append(t)
print("tick \ttimers")
for k, v in interrupts.items():
    print(f"{k}:\t{v}")
print(len(interrupts.keys()))
