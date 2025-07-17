#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
} TaskDescriptor_t;

#define number_of_timers 2
#define number_of_tasks 350
#define HYPERPERIOD 1000
#define NUM_INTERRUPTS 700
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL 2
extern const BaseType_t is_harmonic_timer[2];
extern const TickType_t timerPeriods[2];
extern const TaskDescriptor_t td[350];
#endif