#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdFALSE};
const TickType_t timerPeriods[1] = {5};
const TaskDescriptor_t td[10] = {{0,5,-1},{0,5,-1},{0,5,-1},{0,10,-1},{0,10,-1},{0,10,-1},{0,25,-1},{0,25,-1},{0,25,-1},{0,25,-1}};