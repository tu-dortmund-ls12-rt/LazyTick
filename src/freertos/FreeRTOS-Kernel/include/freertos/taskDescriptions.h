#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
    TickType_t executionTime;
} TaskDescriptor_t;

#define tick(i) (i*159999U)

#define number_of_timers 1
#define number_of_tasks 5
#define HYPERPERIOD (2*number_of_tasks)
#define NUM_INTERRUPTS 60
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL number_of_tasks
extern const BaseType_t is_harmonic_timer[1];
extern const TickType_t timerPeriods[1];
extern const TaskDescriptor_t td[number_of_tasks];
#endif