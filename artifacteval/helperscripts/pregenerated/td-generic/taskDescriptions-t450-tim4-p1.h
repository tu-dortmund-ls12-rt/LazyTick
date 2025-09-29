#ifndef taskDescriptons_H
#define taskDescriptons_H
#include "portmacro.h"
#include "projdefs.h"

typedef struct {
    UBaseType_t timer;
    TickType_t period;
    UBaseType_t taskPos;
} TaskDescriptor_t;

#define number_of_timers 4
#define number_of_tasks 450
#define HYPERPERIOD 300300
#define NUM_INTERRUPTS 153360
#define PERIOD_FACTOR 1
#define ONESHOT_INITIAL 5
extern const BaseType_t is_harmonic_timer[4];
extern const TickType_t timerPeriods[4];
extern const TaskDescriptor_t td[450];
#endif