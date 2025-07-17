#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdFALSE,pdFALSE,pdFALSE,pdTRUE};
const TickType_t timerPeriods[4] = {5,13,11,14};
const TaskDescriptor_t td[20] = {{0,5,-1},{0,5,-1},{0,15,-1},{0,20,-1},{0,25,-1},{0,25,-1},{0,25,-1},{0,35,-1},{0,55,-1},{1,13,-1},{1,26,-1},{1,65,-1},{2,11,-1},{2,11,-1},{2,22,-1},{2,33,-1},{3,14,0},{3,14,1},{3,14,2},{3,28,3}};