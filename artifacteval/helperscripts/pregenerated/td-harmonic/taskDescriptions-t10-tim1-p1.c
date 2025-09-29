#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdTRUE};
const TickType_t timerPeriods[1] = {5};
const TaskDescriptor_t td[10] = {{0,5,0},{0,5,1},{0,5,2},{0,10,3},{0,10,4},{0,10,5},{0,80,6},{0,80,7},{0,80,8},{0,80,9}};