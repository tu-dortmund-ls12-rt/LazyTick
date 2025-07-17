#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdTRUE,pdTRUE,pdTRUE,pdFALSE};
const TickType_t timerPeriods[4] = {22,14,13,5};
const TaskDescriptor_t td[10] = {{0,22,0},{1,14,0},{1,14,1},{2,13,0},{3,5,-1},{3,5,-1},{3,25,-1},{3,25,-1},{3,25,-1},{3,35,-1}};