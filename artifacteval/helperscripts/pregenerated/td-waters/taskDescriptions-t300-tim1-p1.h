#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
} TaskDescriptor_t;

#define number_of_timers 1
#define number_of_tasks 300
#define HYPERPERIOD 1000
#define NUM_INTERRUPTS 1000
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL 1
extern const BaseType_t is_harmonic_timer[1];
extern const TickType_t timerPeriods[1];
extern const TaskDescriptor_t td[300];
#endif