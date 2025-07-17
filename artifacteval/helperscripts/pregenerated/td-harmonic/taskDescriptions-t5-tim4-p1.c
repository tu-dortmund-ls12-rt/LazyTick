#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[3] = {pdTRUE,pdTRUE,pdTRUE};
const TickType_t timerPeriods[3] = {14,22,5};
const TaskDescriptor_t td[5] = {{0,14,0},{1,22,0},{2,5,0},{2,80,1},{2,80,2}};