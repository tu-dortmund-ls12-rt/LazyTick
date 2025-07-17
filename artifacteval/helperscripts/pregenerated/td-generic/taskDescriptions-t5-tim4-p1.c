#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {5,14,22};
const TaskDescriptor_t td[5] = {{0,5,0},{0,25,1},{0,25,2},{1,14,0},{2,22,0}};