#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {11,7,5};
const TaskDescriptor_t td[20] = {{0,11,0},{0,176,1},{0,176,2},{1,7,0},{1,7,1},{1,7,2},{1,14,3},{1,28,4},{1,112,5},{2,5,0},{2,5,1},{2,10,2},{2,10,3},{2,10,4},{2,20,5},{2,40,6},{2,40,7},{2,80,8},{2,80,9},{2,80,10}};