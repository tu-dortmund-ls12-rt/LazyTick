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
#define number_of_tasks 345
#define HYPERPERIOD 560
#define NUM_INTERRUPTS 192
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL 5
extern const BaseType_t is_harmonic_timer[2];
extern const TickType_t timerPeriods[2];
extern const TaskDescriptor_t td[345];
#endif