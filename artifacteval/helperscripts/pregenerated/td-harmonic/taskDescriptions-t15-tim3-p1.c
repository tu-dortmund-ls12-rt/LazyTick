#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {5,7,11};
const TaskDescriptor_t td[15] = {{0,5,0},{0,5,1},{0,10,2},{0,10,3},{0,20,4},{0,80,5},{0,80,6},{0,80,7},{1,7,0},{1,7,1},{1,14,2},{1,112,3},{2,11,0},{2,176,1},{2,176,2}};