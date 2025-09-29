#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {7,5};
const TaskDescriptor_t td[20] = {{0,7,0},{0,7,1},{0,7,2},{0,14,3},{0,14,4},{0,28,5},{0,112,6},{0,112,7},{1,5,0},{1,5,1},{1,10,2},{1,10,3},{1,10,4},{1,20,5},{1,40,6},{1,40,7},{1,80,8},{1,80,9},{1,80,10},{1,80,11}};