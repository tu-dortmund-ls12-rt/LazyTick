#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[4] = {pdTRUE,pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[4] = {13,11,5,14};
const TaskDescriptor_t td[20] = {{0,13,0},{0,26,1},{0,208,2},{1,11,0},{1,11,1},{1,22,2},{1,44,3},{1,176,4},{2,5,0},{2,5,1},{2,20,2},{2,40,3},{2,80,4},{2,80,5},{2,80,6},{3,14,0},{3,14,1},{3,14,2},{3,56,3},{3,112,4}};