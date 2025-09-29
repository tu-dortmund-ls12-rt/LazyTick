#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdFALSE,pdTRUE};
const TickType_t timerPeriods[2] = {5,14};
const TaskDescriptor_t td[5] = {{0,5,-1},{0,10,-1},{0,25,-1},{0,25,-1},{1,14,0}};