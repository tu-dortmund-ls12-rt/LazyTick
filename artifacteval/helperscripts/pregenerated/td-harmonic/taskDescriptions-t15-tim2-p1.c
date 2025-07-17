#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {5,7};
const TaskDescriptor_t td[15] = {{0,5,0},{0,5,1},{0,10,2},{0,10,3},{0,40,4},{0,80,5},{0,80,6},{0,80,7},{0,80,8},{1,7,0},{1,7,1},{1,14,2},{1,14,3},{1,28,4},{1,112,5}};