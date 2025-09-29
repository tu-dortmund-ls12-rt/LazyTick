#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {7,5};
const TaskDescriptor_t td[10] = {{0,7,0},{0,14,1},{1,5,0},{1,5,1},{1,10,2},{1,10,3},{1,80,4},{1,80,5},{1,80,6},{1,80,7}};