#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdTRUE};
const TickType_t timerPeriods[1] = {5};
const TaskDescriptor_t td[15] = {{0,5,0},{0,5,1},{0,5,2},{0,5,3},{0,10,4},{0,10,5},{0,10,6},{0,10,7},{0,20,8},{0,40,9},{0,80,10},{0,80,11},{0,80,12},{0,80,13},{0,80,14}};