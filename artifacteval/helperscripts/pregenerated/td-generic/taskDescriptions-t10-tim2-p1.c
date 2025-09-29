#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdFALSE};
const TickType_t timerPeriods[2] = {7,5};
const TaskDescriptor_t td[10] = {{0,7,0},{0,14,1},{1,5,-1},{1,5,-1},{1,10,-1},{1,10,-1},{1,25,-1},{1,25,-1},{1,25,-1},{1,25,-1}};