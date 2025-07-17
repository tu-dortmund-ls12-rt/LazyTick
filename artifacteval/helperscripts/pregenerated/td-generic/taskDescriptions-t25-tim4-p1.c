#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdFALSE,pdFALSE,pdFALSE,pdTRUE};
const TickType_t timerPeriods[4] = {13,5,11,14};
const TaskDescriptor_t td[25] = {{0,13,-1},{0,26,-1},{0,65,-1},{0,65,-1},{1,5,-1},{1,5,-1},{1,15,-1},{1,20,-1},{1,20,-1},{1,25,-1},{1,25,-1},{1,25,-1},{1,25,-1},{1,35,-1},{1,55,-1},{2,11,-1},{2,11,-1},{2,11,-1},{2,22,-1},{2,33,-1},{2,55,-1},{3,14,0},{3,14,1},{3,14,2},{3,28,3}};