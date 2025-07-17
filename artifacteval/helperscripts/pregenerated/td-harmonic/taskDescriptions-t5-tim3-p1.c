#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {5,11};
const TaskDescriptor_t td[5] = {{0,5,0},{0,10,1},{0,20,2},{1,11,0},{1,176,1}};