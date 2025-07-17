import os
import random

from gurobipy import GRB
from helper import (PRIMES, gen_task_timer_mapping, gen_td, run_model,
                    setup_parser)
from numpy import lcm

parser = setup_parser()
args = parser.parse_args()

PERIOD_FACTOR = args.period_factor
TIMERS = args.timers
NUM_TASKS = args.tasks

RAND_FACTOR = 5

OUTPUTFOLDER = os.path.abspath('td-harmonic/')
if not os.path.exists(OUTPUTFOLDER):
    os.makedirs(OUTPUTFOLDER)

CSVFILE = os.path.join(OUTPUTFOLDER, "miqcp-eval-harmonic.csv")

random.seed(42)


TASKS_BASE_PERIOD = [p*PERIOD_FACTOR for p in PRIMES[:TIMERS]]
harmonics = [[p*2**h for h in range(0, RAND_FACTOR)] for p in TASKS_BASE_PERIOD]
TASKS = [random.choice(random.choice(harmonics)) for _ in range(NUM_TASKS)]

H = int(lcm.reduce(TASKS))

ilp, p, u = run_model(TIMERS, TASKS, H)


###### GENERATE OUTPUT ######

if ilp.Status == GRB.INFEASIBLE:
    raise Exception("Model is infeasible")

if ilp.Status == GRB.OPTIMAL:
    # get task mappings
    mapping_task_timer = gen_task_timer_mapping(ilp, TASKS)

    # generate taskDescription File
    gen_td(mapping_task_timer, NUM_TASKS, TIMERS, PERIOD_FACTOR, RAND_FACTOR, OUTPUTFOLDER, CSVFILE, H, ilp, TASKS_BASE_PERIOD)
