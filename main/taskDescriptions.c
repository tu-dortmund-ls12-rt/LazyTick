#include "freertos/taskDescriptions.h"
const BaseType_t is_harmonic_timer[1] = {pdTRUE};
const TickType_t timerPeriods[1] = {number_of_tasks};
const TaskDescriptor_t td[number_of_tasks] = {{0,number_of_tasks,0,tick(1)},{0,number_of_tasks,1,tick(1)},{0,number_of_tasks,2,tick(1)},{0,number_of_tasks,3,tick(1)},{0,2*number_of_tasks,4,tick(2)-1500}};