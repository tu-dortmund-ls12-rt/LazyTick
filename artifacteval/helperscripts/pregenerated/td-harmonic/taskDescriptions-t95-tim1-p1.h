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
#define number_of_tasks 95
#define HYPERPERIOD 80
#define NUM_INTERRUPTS 16
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL 5
extern const BaseType_t is_harmonic_timer[1];
extern const TickType_t timerPeriods[1];
extern const TaskDescriptor_t td[95];
#endif