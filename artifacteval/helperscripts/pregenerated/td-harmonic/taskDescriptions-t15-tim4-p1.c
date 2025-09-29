#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdTRUE,pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[4] = {11,5,13,14};
const TaskDescriptor_t td[15] = {{0,11,0},{0,22,1},{0,44,2},{1,5,0},{1,5,1},{1,80,2},{1,80,3},{1,80,4},{2,13,0},{2,26,1},{2,208,2},{3,14,0},{3,14,1},{3,56,2},{3,112,3}};