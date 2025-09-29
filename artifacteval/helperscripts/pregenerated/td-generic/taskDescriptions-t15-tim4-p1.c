#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdFALSE,pdTRUE,pdFALSE,pdTRUE};
const TickType_t timerPeriods[4] = {11,14,5,13};
const TaskDescriptor_t td[15] = {{0,11,-1},{0,22,-1},{0,33,-1},{1,14,0},{1,14,1},{1,28,2},{2,5,-1},{2,5,-1},{2,25,-1},{2,25,-1},{2,25,-1},{2,35,-1},{2,65,-1},{3,13,0},{3,26,1}};