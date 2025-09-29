#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdTRUE};
const TickType_t timerPeriods[1] = {5};
const TaskDescriptor_t td[20] = {{0,5,0},{0,5,1},{0,5,2},{0,5,3},{0,5,4},{0,10,5},{0,10,6},{0,10,7},{0,10,8},{0,10,9},{0,20,10},{0,20,11},{0,40,12},{0,40,13},{0,80,14},{0,80,15},{0,80,16},{0,80,17},{0,80,18},{0,80,19}};