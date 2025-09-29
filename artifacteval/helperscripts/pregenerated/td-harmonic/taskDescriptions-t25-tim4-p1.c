#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdTRUE,pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[4] = {14,13,11,5};
const TaskDescriptor_t td[25] = {{0,14,0},{0,14,1},{0,14,2},{0,56,3},{0,112,4},{1,13,0},{1,26,1},{1,208,2},{1,208,3},{2,11,0},{2,11,1},{2,11,2},{2,22,3},{2,44,4},{2,176,5},{2,176,6},{3,5,0},{3,5,1},{3,20,2},{3,40,3},{3,40,4},{3,80,5},{3,80,6},{3,80,7},{3,80,8}};