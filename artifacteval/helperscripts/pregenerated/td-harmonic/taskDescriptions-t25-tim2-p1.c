#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[2] = {pdTRUE,pdTRUE};
const TickType_t timerPeriods[2] = {5,7};
const TaskDescriptor_t td[25] = {{0,5,0},{0,5,1},{0,10,2},{0,10,3},{0,10,4},{0,20,5},{0,40,6},{0,40,7},{0,40,8},{0,80,9},{0,80,10},{0,80,11},{0,80,12},{0,80,13},{1,7,0},{1,7,1},{1,7,2},{1,7,3},{1,14,4},{1,14,5},{1,28,6},{1,112,7},{1,112,8},{1,112,9},{1,112,10}};