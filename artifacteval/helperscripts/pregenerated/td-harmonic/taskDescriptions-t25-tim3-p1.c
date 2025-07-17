#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {11,7,5};
const TaskDescriptor_t td[25] = {{0,11,0},{0,11,1},{0,88,2},{0,176,3},{0,176,4},{1,7,0},{1,7,1},{1,7,2},{1,7,3},{1,14,4},{1,28,5},{1,112,6},{1,112,7},{2,5,0},{2,5,1},{2,10,2},{2,10,3},{2,10,4},{2,20,5},{2,20,6},{2,40,7},{2,40,8},{2,80,9},{2,80,10},{2,80,11}};