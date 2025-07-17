#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdFALSE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {5,11,7};
const TaskDescriptor_t td[10] = {{0,5,-1},{0,5,-1},{0,10,-1},{0,10,-1},{0,15,-1},{0,25,-1},{1,11,0},{1,55,1},{1,55,2},{2,7,0}};