#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {11,7,5};
const TaskDescriptor_t td[10] = {{0,11,0},{0,176,1},{0,176,2},{1,7,0},{2,5,0},{2,5,1},{2,10,2},{2,10,3},{2,20,4},{2,80,5}};