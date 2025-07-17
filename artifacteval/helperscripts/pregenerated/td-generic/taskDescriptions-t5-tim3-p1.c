#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdFALSE};
const TickType_t timerPeriods[2] = {11,5};
const TaskDescriptor_t td[5] = {{0,11,0},{1,5,-1},{1,10,-1},{1,15,-1},{1,55,-1}};