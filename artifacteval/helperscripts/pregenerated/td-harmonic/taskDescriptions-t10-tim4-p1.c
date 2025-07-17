#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdTRUE,pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[4] = {14,13,5,22};
const TaskDescriptor_t td[10] = {{0,14,0},{0,14,1},{0,112,2},{1,13,0},{2,5,0},{2,5,1},{2,80,2},{2,80,3},{2,80,4},{3,22,0}};