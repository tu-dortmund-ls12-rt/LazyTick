#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdTRUE};
const TickType_t timerPeriods[1] = {5};
const TaskDescriptor_t td[5] = {{0,5,0},{0,10,1},{0,10,2},{0,80,3},{0,80,4}};