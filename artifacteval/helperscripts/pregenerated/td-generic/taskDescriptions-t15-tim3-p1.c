#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdFALSE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {5,7,11};
const TaskDescriptor_t td[15] = {{0,5,-1},{0,5,-1},{0,10,-1},{0,10,-1},{0,15,-1},{0,25,-1},{0,25,-1},{0,25,-1},{0,35,-1},{0,55,-1},{1,7,0},{1,7,1},{1,14,2},{2,11,0},{2,55,1}};