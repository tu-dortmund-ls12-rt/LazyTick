#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {14,5};
const TaskDescriptor_t td[5] = {{0,14,0},{1,5,0},{1,10,1},{1,80,2},{1,80,3}};