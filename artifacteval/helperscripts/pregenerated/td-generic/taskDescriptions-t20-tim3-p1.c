#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdFALSE,pdFALSE};
const TickType_t timerPeriods[3] = {11,7,5};
const TaskDescriptor_t td[20] = {{0,11,0},{1,7,-1},{1,7,-1},{1,7,-1},{1,14,-1},{1,21,-1},{1,35,-1},{2,5,-1},{2,5,-1},{2,10,-1},{2,10,-1},{2,10,-1},{2,15,-1},{2,20,-1},{2,20,-1},{2,25,-1},{2,25,-1},{2,25,-1},{2,55,-1},{2,55,-1}};