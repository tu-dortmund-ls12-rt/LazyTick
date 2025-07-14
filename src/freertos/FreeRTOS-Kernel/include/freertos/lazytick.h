#ifndef lazytick_H
#define lazytick_H

#include "freertos/taskDescriptions.h"
#include "esp_cpu.h"

#define ETS_FROM_CPU_INTR0_SOURCE_NO 9
#define ETS_SYSTIMER_TARGET0_INTR_SOURCE_NO 3
#define ETS_TG0_T0_LEVEL_INTR_SOURCE_NO 3
#define ETS_TG0_T1_LEVEL_INTR_SOURCE_NO 12
#define ETS_TG1_T0_LEVEL_INTR_SOURCE_NO 13
#define ETS_TG1_T1_LEVEL_INTR_SOURCE_NO 17


typedef uint16_t TimerNum;

// extern uint32_t yield_ctr;
extern uint32_t deadline_misses;
// extern uint32_t dct2;
// extern uint32_t dct3;

uint32_t get_num_tasks_per_timer(TimerNum tn);
TaskDescriptor_t* get_td_per_timer(TimerNum tn);
void prepare_td();
void printOutput();
#ifdef SYSTICK_DISABLED
extern const TickType_t timerPeriods[number_of_timers];

// INFO block function
#ifdef SYSTICK_DISABLED
BaseType_t block(TimerNum tn, TickType_t* const pxPreviousWakeTime, const TickType_t period, const UBaseType_t task_pos, uint32_t* old_buffer_pos);
#else
BaseType_t block(TimerNum tn, TickType_t* const pxPreviousWakeTime, const TickType_t period);
#endif
BaseType_t manageTimerList(TimerNum tn);

TickType_t getTimerTick(TimerNum tn);
extern uint32_t num_items_in_delayed[number_of_timers];
extern uint32_t num_items_in_deadline_misses[number_of_timers];

extern void start_gptimers();

#else
extern uint32_t num_items_in_delayed;
extern uint32_t num_items_in_deadline_misses;
#endif  // SYSTICK_DISABLED
#ifdef ONESHOT
extern void start_oneshot();
extern void update_oneshot(TickType_t nextAlarm);
extern void update_oneshotISR(TickType_t nextAlarm,TickType_t xTickCount);
extern TickType_t currentAlarmTick;
extern TickType_t lastAlarm;
#endif

#if defined(BENCH_TP_ISR_ALL) || defined(BENCH_TP_ISR_HANDLER)
// #ifdef DEBUG
// typedef struct {
//     esp_cpu_cycle_count_t ccycle;
//     TimerNum timer;
//     TickType_t timerPeriod;
//     TickType_t tick;
// } Debug_t;
// extern Debug_t *tp_debug;
// extern size_t debug_ctr;
// void printDebug();
// #endif
extern esp_cpu_cycle_count_t* tp_ccycles;
#ifdef ENABLE_TASK_TRACE
extern char** tp_tasks;
#endif
extern size_t timepoint_ctr0;
extern size_t timepoint_ctr1;
#endif  // defined(BENCH_TP_ISR_ALL) || defined(BENCH_TP_ISR_HANDLER)

extern int64_t start_tp;

#ifdef BENCH_INSERT
extern esp_cpu_cycle_count_t* insertion_times;
extern size_t insert_ctr;
// block tp

extern esp_cpu_cycle_count_t* retrieval_times;
extern size_t retrieval_ctr;
// isr tp
#endif

#ifdef BENCH_TP_ISR_ALL
// global interrupt tp
extern void save_timepoint_start(void);
extern void save_timepoint_start2(void);
extern void save_timepoint_start3(void);
extern void save_timepoint_start4(void);
extern void save_timepoint_start5(void);
extern void save_timepoint_start6(void);
extern void save_timepoint_end(void);
extern void save_timepoint_end_nesting(void);
#endif

#endif