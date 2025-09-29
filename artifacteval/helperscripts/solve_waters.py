import argparse
import os
from collections import defaultdict

import gurobipy as gp
from gurobipy import GRB, Model, quicksum
from numpy import lcm


class TimerInfo:
    def __init__(self, number: int, period: int, is_harmonic: bool = False, tasks: list[int] = [], slots: int = -1, num_tasks: int = -1):
        self.number = number
        self.__period = period
        self.__is_harmonic = is_harmonic
        self.__tasks = tasks
        self.__slots = slots
        self.__num_tasks = num_tasks

    def __repr__(self):
        return (f"TimerInfo(number={self.number}, period={self.__period}, "
                f"is_harmonic={self.__is_harmonic}, tasks={self.__tasks}, "
                f"slots={self.__slots}, num_tasks={self.__num_tasks})")

    def set_tasks(self, tasks: list[int]):
        self.__tasks = sorted(tasks)
        # check if tasks are harmonic
        is_harmonic = True
        for n1 in self.__tasks:
            for n2 in [n for n in self.__tasks if n >= n1]:
                if n2 % n1 != 0:
                    is_harmonic = False
                    break
        if is_harmonic:
            self.__is_harmonic = True

        if self.__is_harmonic:
            self.__num_tasks = len(tasks)
            self.__slots = len(tasks)
        else:
            self.__num_tasks = len(tasks)
            self.__slots = max(tasks)//self.__period

    def set_period(self, period: int):
        self.__period = period
        self.set_tasks(self.__tasks)

    def gen_c_td_entry(self) -> str:
        code = []
        if self.__is_harmonic:
            for i, task in enumerate(self.__tasks):
                code.append('{' + str(self.number) + ',' + str(task) + ',' + str(i) + '}')
        else:
            for task in self.__tasks:
                code.append('{' + str(self.number) + ',' + str(task) + ',-1}')
        return ','.join(code)

    @property
    def tasks(self) -> list[int]:
        return self.__tasks

    @property
    def num_tasks(self) -> int:
        return self.__num_tasks

    @property
    def slots(self) -> int:
        return self.__slots

    @property
    def is_harmonic(self) -> bool:
        return self.__is_harmonic

    @property
    def period(self) -> int:
        return self.__period


STRUCT_DEF = r'''#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
} TaskDescriptor_t;
'''


PRIMES = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]

TASKS50 = [2, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 1000, 1000]
TASKS100 = [2, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS150 = [2, 2, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 1000, 1000, 1000, 1000]
TASKS200 = [2, 2, 2, 2, 2, 2, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS250 = [2, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS300 = [2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS350 = [2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS400 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS450 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
TASKS500 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
            20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]

WATERS = [TASKS50, TASKS100, TASKS150, TASKS200, TASKS250, TASKS300, TASKS350, TASKS400, TASKS450, TASKS500]


def setup_parser():
    parser = argparse.ArgumentParser(description="Parse timers, tasks, period factor")

    parser.add_argument("--timers", type=int, required=True)
    parser.add_argument("--tasks", type=int, required=True)
    parser.add_argument("--period_factor", type=int, required=False, default=1)
    return parser


def run_model(TIMERS: int, TASKS: list[int], H: int) -> Model:
    ilp = gp.Model()

    ilp.Params.NodefileStart = 1
    ilp.Params.MIPGap = 0
    ilp.Params.MIPGapAbs = 0
    # ilp.Params.TimeLimit = 10*60

    p = ilp.addVars(TIMERS, lb=1, ub=max(TASKS), vtype=GRB.INTEGER, name="p")
    u = ilp.addVars(TIMERS, vtype=GRB.BINARY, name="u")
    m = ilp.addVars(range(len(TASKS)), range(TIMERS), vtype=GRB.BINARY, name="m")
    d = ilp.addVars(range(len(TASKS)), lb=1, vtype=GRB.INTEGER, name="d")
    h = ilp.addVars(range(len(TASKS)), range(TIMERS), lb=0, ub=max(TASKS), vtype=GRB.INTEGER, name="helperForDivisor")

    for t in range(len(TASKS)):
        d[t].ub = TASKS[t]

    # the upper bound breaks the model if it is too large
    if H > (1 << 32):
        f = ilp.addVars(TIMERS, vtype=GRB.CONTINUOUS, name="f")
        for j in range(TIMERS):
            ilp.addConstr(f[j]*p[j] == 1)
    else:
        f = ilp.addVars(TIMERS, lb=H/max(TASKS), ub=H, vtype=GRB.INTEGER, name="f")
        for j in range(TIMERS):
            ilp.addConstr(f[j]*p[j] == H)

    for i in range(len(TASKS)):
        ilp.addConstr(1 == quicksum([m[i, j] for j in range(TIMERS)]))

    for j in range(TIMERS):
        ilp.addGenConstrOr(u[j], [m[i, j] for i in range(len(TASKS))], name=f"useTimer{j}")

    # helper as gurobi does not support ternary expressions
    for i in range(len(TASKS)):
        for j in range(TIMERS):
            ilp.addConstr(h[i, j] == p[j]*m[i, j])

    for i in range(len(TASKS)):
        ilp.addConstr(d[i]*quicksum([h[i, j] for j in range(TIMERS)]) == TASKS[i])

    # minimize number of timer interrupts per hyperperiod
    ilp.setObjective(quicksum([f[j]*u[j] for j in range(TIMERS)]), GRB.MINIMIZE)

    ilp.optimize()
    return ilp, p, u


def gen_task_timer_mapping(ilp: Model, TASKS: list[int]) -> list[dict]:
    mapping_task_timer = []
    for i in ilp.getVars():
        if i.VarName.startswith('m') and i.X == 1.0:
            task, timer = i.VarName.split('[')[1].split(']')[0].split(',')
            task = int(task)
            timer = int(timer)
            mapping_task_timer.append({'task': task, 'period': int(TASKS[task]), 'timer': timer})
    return mapping_task_timer


def gen_td(mapping_task_timer: list[dict], NUM_TASKS: int, TIMERS: int, PERIOD_FACTOR: int, RAND_FACTOR: int, OUTPUTFOLDER: str, CSVFILE: str, H: int, ilp: Model, TASKS_BASE_PERIOD: list[int]) -> None:

    timers = []
    for i in ilp.getVars():
        if i.VarName.startswith('u') and i.X == 1.0:
            timernum = int(i.VarName.split('[')[1].split(']')[0].split(',')[0])
            timerperiod = int(ilp.getVarByName(f'p[{timernum}]').X)
            timers.append(TimerInfo(timernum, timerperiod))

    tmp_tasks = defaultdict(list)
    for task in mapping_task_timer:
        tmp_tasks[task['timer']].append(task['period'])
    for timer in timers:
        timer.set_tasks(tmp_tasks[timer.number])
    for i, timer in enumerate(timers):
        timer.number = i
    print(timers)
    if len(timers) > 2:
        raise IndexError

    c_is_harmonic = f'const BaseType_t is_harmonic_timer[{len(timers)}] = '+'{' + ','.join(['pdTRUE' if t.is_harmonic else 'pdFALSE' for t in timers])+'};\n'
    c_timer_periods = f'const TickType_t timerPeriods[{len(timers)}] = '+'{' + ','.join([str(t.period) for t in timers]) + '};\n'

    tasksPerTimer = [(t.number, t.num_tasks) for t in timers]
    timerPeriods = [(t.number, t.period) for t in timers]

    num_interrupts = sum([int(H/t.period) for t in timers])

    if not os.path.exists(CSVFILE):
        with open(CSVFILE, "w") as f:
            f.write("Number of Tasks;Number of Timers;Random Factor;Hyperperiod;Number of Interrupts;Task Base Periods;Timer Periods;Tasks per Timer;Model Fingerprint;Model Runtime;H Workaround\n")

    with open(CSVFILE, "a") as f:
        f.write(f"{NUM_TASKS};{TIMERS};{RAND_FACTOR};{H};{num_interrupts};{TASKS_BASE_PERIOD};{timerPeriods};{tasksPerTimer};{hex(ilp.Fingerprint & 0xFFFFFFFF)};{ilp.Runtime};{H > (1 << 32)}\n")

    # write output
    with open(f"{OUTPUTFOLDER}/taskDescriptions-t{NUM_TASKS}-tim{TIMERS}-p{PERIOD_FACTOR}.h", "w") as f:
        f.write(STRUCT_DEF + '\n')
        f.write(f'#define number_of_timers {len(timers)}\n')
        f.write(f'#define number_of_tasks {NUM_TASKS}\n')
        f.write(f'#define HYPERPERIOD {H}\n')
        f.write(f'#define NUM_INTERRUPTS {num_interrupts}\n')
        f.write(f'#define PERIOD_FACTOR {PERIOD_FACTOR}\n')
        f.write(f'#define ONESHOT_INITIAL {min(timerPeriods, key=lambda x: x[1])[1]}\n')
        f.write(f'extern const BaseType_t is_harmonic_timer[{len(timers)}];\n')
        f.write(f'extern const TickType_t timerPeriods[{len(timers)}];\n')
        f.write(f'extern const TaskDescriptor_t td[{NUM_TASKS}];\n')
        f.write('#endif')

    c_tds = 'const TaskDescriptor_t td['+str(NUM_TASKS)+'] = {' + ','.join([t.gen_c_td_entry() for t in timers]) + '};'

    with open(f"{OUTPUTFOLDER}/taskDescriptions-t{NUM_TASKS}-tim{TIMERS}-p{PERIOD_FACTOR}.c", "w") as f:
        f.write('#include "freertos/taskDescriptions.h"\n')
        f.write(c_is_harmonic)
        f.write(c_timer_periods)
        f.write(c_tds)


OUTPUTFOLDER = os.path.abspath('td-waters/')
if not os.path.exists(OUTPUTFOLDER):
    os.makedirs(OUTPUTFOLDER)

CSVFILE = os.path.join(OUTPUTFOLDER, "miqcp-eval-waters.csv")

for t in WATERS:
    for timer in [1, 2]:
        h = int(lcm.reduce(t))

        ilp, p, u = run_model(timer, t, h)

        ###### GENERATE OUTPUT ######

        if ilp.Status == GRB.INFEASIBLE:
            raise Exception("Model is infeasible")

        if ilp.Status == GRB.OPTIMAL:
            # get task mappings
            mapping_task_timer = gen_task_timer_mapping(ilp, t)

            # generate taskDescription File
            gen_td(mapping_task_timer, len(t), timer, 1, 1, OUTPUTFOLDER, CSVFILE, h, ilp, [])
