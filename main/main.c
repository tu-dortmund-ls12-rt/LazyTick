#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef ENERGY_TEST
#include "driver/gpio.h"
#endif
#include "driver/gptimer.h"
#include "esp_attr.h"
#include "esp_cpu.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "string.h"
#define TASK_STACK_SIZE 4096
// tp_len is naturally bounded ex: we only run 60s => 60000 ticks => 120000 elements
#define TP_LEN (NUM_TICKS * 3)
#define TASK_PRIO 3

uint32_t deadline_misses = 0;
int64_t start_tp = 0;
int64_t end_tp = 0;
TaskHandle_t taskHandles[number_of_tasks];
SemaphoreHandle_t semOutput;
bool tasks_deleted = pdFALSE;
uint32_t intr_bits = 0;
#ifdef ONESHOT
TickType_t currentAlarmTick = ONESHOT_INITIAL;
TickType_t lastAlarm = 0;
#endif

#ifdef BENCH_INSERT
// uint64_t insert_time = 0;
#define INSERT_LEN (NUM_TICKS * number_of_tasks * 2)
esp_cpu_cycle_count_t *insertion_times;
size_t insert_ctr = 0;

// uint64_t retrieval_time = 0;
esp_cpu_cycle_count_t *retrieval_times;
size_t retrieval_ctr = 0;
#endif

#if defined(BENCH_TP_ISR_ALL) || defined(BENCH_TP_ISR_HANDLER)
esp_cpu_cycle_count_t *tp_ccycles;
// #ifdef DEBUG
// Debug_t *tp_debug;
// #endif
#ifdef ENABLE_TASK_TRACE
char **tp_tasks;
#endif
// this encodes the marker through index positions
size_t timepoint_ctr0 = 0;
size_t timepoint_ctr1 = 1;
size_t debug_ctr = 0;
#endif  // defined(BENCH_TP_ISR_ALL) || defined(BENCH_TP_ISR_HANDLER)

#ifdef SYSTICK_DISABLED
gptimer_handle_t timerHandles[number_of_timers];

int getTimerSrc(TimerNum tn) {
    switch (tn) {
        case 0:
            return ETS_TG0_T0_LEVEL_INTR_SOURCE_NO;
        case 1:
            return ETS_TG0_T1_LEVEL_INTR_SOURCE_NO;
        case 2:
            return ETS_TG1_T0_LEVEL_INTR_SOURCE_NO;
        case 3:
            return ETS_TG1_T1_LEVEL_INTR_SOURCE_NO;
        default:
            abort();
    }
}
// Task Parameters
typedef struct {
    TimerNum timerNum;
    TickType_t period;
    uint16_t taskNum;
    UBaseType_t taskPos;
    uint32_t initial_buffer_pos;
#if (DEADLINE_TEST == 1)
    TickType_t executionTime;
#endif
} TaskParams_t;
#elif defined(ONESHOT)

gptimer_handle_t oneshotHandle;

int getTimerSrc() {
    return ETS_TG0_T0_LEVEL_INTR_SOURCE_NO;
}
// Task Parameters
typedef struct {
    TickType_t period;
    uint16_t taskNum;
#if (DEADLINE_TEST == 1)
    TickType_t executionTime;
#endif
} TaskParams_t;
#else
// Task Parameters
#if (DEADLINE_TEST == 1)
typedef struct {
    TickType_t period;
    uint16_t taskNum;
    TickType_t executionTime;
} TaskParams_t;
#else
typedef struct {
    TickType_t period;
    uint16_t taskNum;
} TaskParams_t;
#endif
#endif  // SYSTICK_DISABLED

// #ifdef DEBUG
// void printDebug() {
//     portDISABLE_INTERRUPTS();
//     for (size_t i = 0; i < debug_ctr; i++) {
//         ESP_DRAM_LOGE("abort debug", "cycle %" PRIu32 ", timer %" PRIu32 ", timerPeriod %" PRIu32 ", tick %" PRIu32, tp_debug[i].ccycle, tp_debug[i].timer, tp_debug[i].timerPeriod, tp_debug[i].tick);
//     }
// }
// #endif

void printOutput(void *pvParameters) {
#ifdef ENERGY_TEST
    gpio_set_level(GPIO_NUM_7, 0);
#endif
    end_tp = esp_timer_get_time();
#ifdef DEBUG
    printDebug();
#endif
#ifdef BENCH_TP_ISR_ALL
    ESP_DRAM_LOGI("output debug", "%lu, %lu", timepoint_ctr0, timepoint_ctr1);
#endif
// printf("yield_ctr: %" PRIu32 " # %lu\n", yield_ctr, (timepoint_ctr1 / 2) - yield_ctr);
// printf("(ctr2,delayed,dct2,dct3): (%lu,%lu,%lu,%lu)\n", ctr2, deadline_misses, dct2, dct3);
#ifdef DEBUG_NUM_ITEMS
#ifdef SYSTICK_DISABLED
    uint32_t nit0 = num_items_in_deadline_misses[0] != 0 ? num_items_in_delayed[0] / num_items_in_deadline_misses[0] : 0;
    uint32_t nit1 = num_items_in_deadline_misses[1] != 0 ? num_items_in_delayed[1] / num_items_in_deadline_misses[1] : 0;
    uint32_t nit2 = num_items_in_deadline_misses[2] != 0 ? num_items_in_delayed[2] / num_items_in_deadline_misses[2] : 0;
    uint32_t nit3 = num_items_in_deadline_misses[3] != 0 ? num_items_in_delayed[3] / num_items_in_deadline_misses[3] : 0;
    printf("debug: avg number of items in delayed list: (%ld,%ld,%ld,%ld)\n", nit0, nit1, nit2, nit3);
#else
    printf("debug: avg number of items in delayed list: %ld\n", num_items_in_delayed / num_items_in_deadline_misses);
#endif
#endif

#if defined(SYSTICK_DISABLED)
    ESP_DRAM_LOGI("output", "test_type=lazytick");
#elif defined(ONESHOT)
    ESP_DRAM_LOGI("output", "test_type=oneshot");
#else
    ESP_DRAM_LOGI("output", "test_type=freertos");
#endif
    ESP_DRAM_LOGI("output", "num_ticks=%d", NUM_TICKS);
    ESP_DRAM_LOGI("output", "period_factor=%d", PERIOD_FACTOR);
    ESP_DRAM_LOGI("output", "number_of_tasks=%d", number_of_tasks);
    ESP_DRAM_LOGI("output", "number_of_timers=%d", number_of_timers);
    char buffer[100] = {0};
    char *ptr = buffer;
    for (int i = 0; i < number_of_timers; i++)
        ptr += sprintf(ptr, "%ld%s", timerPeriods[i], (i == number_of_timers - 1) ? "" : ",");
    ESP_DRAM_LOGI("output", "timer_periods=%s", buffer);
    memset(buffer, 0, sizeof(buffer));
    ptr = buffer;
    for (int i = 0; i < number_of_timers; i++)
        ptr += sprintf(ptr, "%s%s", is_harmonic_timer[i] ? "True" : "False", (i == number_of_timers - 1) ? "" : ",");

    ESP_DRAM_LOGI("output", "timer_harmonic=%s", buffer);
    ESP_DRAM_LOGI("output", "time_us(start_tp,end_tp,duration)=%" PRId64 ",%" PRId64 ",%" PRId64, start_tp, end_tp, end_tp - start_tp);
    ESP_DRAM_LOGI("output", "deadline_misses=%" PRIu32 "", deadline_misses);

    ESP_DRAM_LOGI("output", "INTERRUPT OUTPUT START");
#if defined(BENCH_TP_ISR_ALL)
    for (size_t i = 0; i < timepoint_ctr1 - 1; i++) {
#ifdef ENABLE_TASK_TRACE
        if (i % 2 == 0)
            ESP_DRAM_LOGI("output", "%zu,%" PRIu32 ",%s,0\n", i, tp_ccycles[i], tp_tasks[i]);
        else
            ESP_DRAM_LOGI("output", "%zu,%" PRIu32 ",%s,1\n", i, tp_ccycles[i], tp_tasks[i]);
#else
        if (i % 2 == 0)
            ESP_DRAM_LOGI("output", "%" PRIu32 ",%" PRIu32 ",,0", i, tp_ccycles[i]);
        else
            ESP_DRAM_LOGI("output", "%" PRIu32 ",%" PRIu32 ",,1", i, tp_ccycles[i]);
#endif
    }
#endif

    ESP_DRAM_LOGI("output", "INTERRUPT OUTPUT END");
#ifdef BENCH_INSERT
    ESP_DRAM_LOGI("output_ins", "INSERT OUTPUT START");
    for (size_t i = 0; i < insert_ctr; i++) {
        ESP_DRAM_LOGI("output_ins", "%" PRIu32 ",%" PRIu32, i, insertion_times[i]);
    }
    ESP_DRAM_LOGI("output_ins", "INSERT OUTPUT END");
    ESP_DRAM_LOGI("output_retr", "RETRIEVAL OUTPUT START");
    for (size_t i = 0; i < retrieval_ctr; i++) {
        ESP_DRAM_LOGI("output_retr", "%" PRIu32 ",%" PRIu32, i, retrieval_times[i]);
    }
    ESP_DRAM_LOGI("output_retr", "RETRIEVAL OUTPUT END");
#endif
    for (;;);
}

void simple(void *pvParameters) {
    const TaskParams_t *params = (TaskParams_t *)pvParameters;

    // Force release time = 0 of all tasks
    TickType_t xLastWakeTime = 0;
#ifdef SYSTICK_DISABLED
    uint32_t old_buffer_pos = params->initial_buffer_pos;
#endif
    for (;;) {
#ifdef SYSTICK_DISABLED
#ifdef DEBUG_INSERT
        ESP_LOGE("insert", "t%" PRIu16 ", tick %" PRIu32, params->taskNum, getTimerTick(params->timerNum));
#endif
        // ESP_LOGI("task", "%" PRIu16 " awake at %" PRIu32, params->taskNum, getTimerTick(params->timerNum));
        block(params->timerNum, &xLastWakeTime, params->period, params->taskPos, &(old_buffer_pos));
#else
#ifdef DEBUG_INSERT
        ESP_LOGE("insert", "t%" PRIu16 ", tick %" PRIu32, params->taskNum, xTaskGetTickCount());
#endif
        // ESP_LOGI("task", "%" PRIu16 " awake at %" PRIu32, params->taskNum, xTaskGetTickCount());
        xTaskDelayUntil(&xLastWakeTime, params->period);
#endif
        for (volatile unsigned long i = 0; i < TASK_IT; i++);
    }
}
#if (DEADLINE_TEST == 1)
void dl_task(void *pvParameters) {
    const TaskParams_t *params = (TaskParams_t *)pvParameters;

    // Force release time = 0 of all tasks
    TickType_t xLastWakeTime = 0;
#ifdef SYSTICK_DISABLED
    uint32_t old_buffer_pos = params->initial_buffer_pos;
#endif
    for (;;) {
        // flags: -O2, 10ms tick, and BENCH_INSERT, BENCH_TP_ISR_ALL disabled
        // taskset: {{0,5,0,tick(1)},{0,5,1,tick(1)},{0,5,2,tick(1)},{0,5,3,tick(1)},{0,10,4,tick(2)}}
        // C5=tick(2)+725 works for lazytick (harmonic)
        // C5=tick(2)+400 works for oneshot
        // C5=tick(2)-1500 works for default
        for (volatile uint32_t i = 0; i < params->executionTime; i++);

        // 10 tasks: C5=tick(2)-1500 breaks default, oneshot+lazytick works
        // 15 tasks: C5=tick(2)-1500 breaks default+oneshot, lazytick works
        // 20 tasks: C5=tick(2)-1500 breaks all

        // TickType_t start = xTaskGetTickCount();
        // esp_cpu_cycle_count_t cstart = esp_cpu_get_cycle_count();
        // for (volatile uint32_t i = 0; i < 159999; i++);  // takes about 2399994 cycles => 10ms=1tick
        // esp_cpu_cycle_count_t cend = esp_cpu_get_cycle_count();
        // TickType_t end = xTaskGetTickCount();
        // ESP_LOGI("task", "t%d ticks %lu cycles %lu done", params->taskNum, end - start, cend - cstart);

#ifdef SYSTICK_DISABLED
        block(params->timerNum, &xLastWakeTime, params->period, params->taskPos, &(old_buffer_pos));
#else
        xTaskDelayUntil(&xLastWakeTime, params->period);
#endif
    }
}
#endif
#if (DEADLINE_TEST == 1)
void createTasks(uint32_t *taskNum, size_t numTasks, TimerNum timer, TickType_t period, uint32_t stack_size, UBaseType_t prio, TaskFunction_t func, const size_t taskPos, TickType_t executionTime) {
#else
void createTasks(uint32_t *taskNum, size_t numTasks, TimerNum timer, TickType_t period, uint32_t stack_size, UBaseType_t prio, TaskFunction_t func, const size_t taskPos) {
#endif
    for (size_t i = 0; i < numTasks; i++) {
        char task_name[16];
        sprintf(task_name, "t%lu", *taskNum);
        // ESP_LOGI("createTask heap free", "%s, total: %" PRIu32 ", overall min: %" PRIu32 ", block internal %zu, block PSRAM %zu", task_name, esp_get_free_heap_size(), esp_get_minimum_free_heap_size(), heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL), heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM));

        // task params is in external RAM
        TaskParams_t *p = (TaskParams_t *)heap_caps_calloc(sizeof(TaskParams_t), 1, MALLOC_CAP_SPIRAM);  // this is never free'd
        if (p == NULL) {
            ESP_LOGE("createTasks", "Not enough memory for TaskParams for task %" PRIu32, *taskNum);
            abort();
        }
        p->taskNum = *taskNum;
        p->period = period;
#ifdef SYSTICK_DISABLED
        p->taskPos = taskPos;
        p->timerNum = timer;
        // set initial buffer position
        p->initial_buffer_pos = (p->period / timerPeriods[p->timerNum]) - 1;
#endif
#if (DEADLINE_TEST == 1)
        p->executionTime = executionTime;
#endif
        // TCB memory must always be in internal memory
        StaticTask_t *ctb = (StaticTask_t *)heap_caps_calloc(sizeof(StaticTask_t), 1, MALLOC_CAP_INTERNAL);
        if (ctb == NULL) {
            ESP_LOGE("createTasks", "Not enough memory for TaskBuffer for task %lu", *taskNum);
            abort();
        }

        // stack memory is in external RAM
        StackType_t *cs = (StackType_t *)heap_caps_calloc(sizeof(StackType_t), stack_size, MALLOC_CAP_SPIRAM);
        if (cs == NULL) {
            ESP_LOGE("createTasks", "Not enough memory for StackBuffer for task %lu", *taskNum);
            abort();
        }

        taskHandles[*taskNum] = xTaskCreateStatic(func, task_name, stack_size, p, prio, cs, ctb, p->period);
        (*taskNum)++;
        printf("created task; %s,%" PRIu32 ",%u,%u, prio: %u\n", task_name, period, timer, taskPos, prio);
    }
}

#ifdef SYSTICK_DISABLED
// time measurements for systick work here as well, as they catch all interrupts
bool IRAM_ATTR timer_callback(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_ctx) {
    const TimerNum tn = *((TimerNum *)user_ctx);
    BaseType_t xSwitchRequired;
    UBaseType_t uxSavedInterruptStatus = portSET_INTERRUPT_MASK_FROM_ISR();

#ifdef BENCH_INSERT
    esp_cpu_cycle_count_t before = esp_cpu_get_cycle_count();
    xSwitchRequired = manageTimerList(tn);
    esp_cpu_cycle_count_t after = esp_cpu_get_cycle_count();
    retrieval_times[retrieval_ctr] = (after - before);
    retrieval_ctr++;
#else
    xSwitchRequired = manageTimerList(tn);
#endif

    // #ifdef DEBUG
    // tp_debug[debug_ctr] = (Debug_t){.ccycle = esp_cpu_get_cycle_count(), .timer = tn, .timerPeriod = timerPeriods[tn], .tick = getTimerTick(tn)};
    // debug_ctr++;
    // #endif

    // instead of running for a whole hyperperiod => run only for 60s always
    if (getTimerTick(tn) >= NUM_TICKS) {
        // disable all timer interrupts
        for (size_t i = 0; i < number_of_timers; i++) {
            esp_intr_disable_source(getTimerSrc(i));
            // clear interrupt bit
            intr_bits &= ~(1U << i);
        }
        // wake deferred output task
        if (intr_bits == 0) {
            printOutput(NULL);
        }
    }
    portCLEAR_INTERRUPT_MASK_FROM_ISR(uxSavedInterruptStatus);
    // if (xSwitchRequired != pdFALSE) {
    //     portYIELD_FROM_ISR();
    // }
    return xSwitchRequired;  // enables yield in gptimer.c
}

gptimer_handle_t IRAM_ATTR init_timer(TimerNum tn) {
    gptimer_handle_t gptimer = NULL;
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1 * 1000 * 1000,  // 1MHz, 1 tick = 1us
    };
    ESP_ERROR_CHECK(gptimer_new_timer(&timer_config, &gptimer));

    gptimer_alarm_config_t alarm_config = {
        .reload_count = 0,                                                     // counter will reload with 0 on alarm event
        .alarm_count = timerPeriods[tn] * 1000 * (1000 / CONFIG_FREERTOS_HZ),  // period = CONFIG_FREERTOS_HZ
        .flags.auto_reload_on_alarm = true,                                    // enable auto-reload
    };
    ESP_ERROR_CHECK(gptimer_set_alarm_action(gptimer, &alarm_config));

    ESP_DRAM_LOGI("timer init", "init timer %ld to period %ld", tn, timerPeriods[tn]);

    gptimer_event_callbacks_t cbs = {
        .on_alarm = timer_callback,  // register user callback
    };

    void *tn_ctx = heap_caps_calloc(sizeof(TimerNum), 1, MALLOC_CAP_32BIT);
    if (tn_ctx == NULL) abort();
    *(TimerNum *)(tn_ctx) = tn;

    ESP_ERROR_CHECK(gptimer_register_event_callbacks(gptimer, &cbs, tn_ctx));
    ESP_ERROR_CHECK(gptimer_enable(gptimer));
    intr_bits |= (1U << tn);
    return gptimer;
}

void start_gptimers() {
    // start only those timers that are required
    for (int i = 0; i < number_of_timers; i++) {
        ESP_ERROR_CHECK(gptimer_start(timerHandles[i]));
    }
    for (int i = 0; i < number_of_timers; i++) {
        ESP_ERROR_CHECK(gptimer_set_raw_count(timerHandles[i], 0));
    }
}
#elif defined(ONESHOT)
bool IRAM_ATTR timer_callback(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_ctx) {
    BaseType_t xSwitchRequired;
    UBaseType_t uxSavedInterruptStatus = portSET_INTERRUPT_MASK_FROM_ISR();

#ifdef BENCH_INSERT
    esp_cpu_cycle_count_t before = esp_cpu_get_cycle_count();
    xSwitchRequired = xTaskIncrementTick();
    esp_cpu_cycle_count_t after = esp_cpu_get_cycle_count();
    retrieval_times[retrieval_ctr] = (after - before);
    retrieval_ctr++;
#else
    xSwitchRequired = xTaskIncrementTick();
#endif
// debug
#ifdef DEBUG
    tp_debug[debug_ctr] = (Debug_t){.ccycle = esp_cpu_get_cycle_count(), .timer = 0, .timerPeriod = -1, .tick = xTaskGetTickCountFromISR()};
    debug_ctr++;
#endif
    // ESP_DRAM_LOGE("callback","%ld",xTaskGetTickCountFromISR());
    // instead of running for a whole hyperperiod => run only for 60s always
    if (xTaskGetTickCountFromISR() >= NUM_TICKS) {
        printOutput(NULL);
    }
    portCLEAR_INTERRUPT_MASK_FROM_ISR(uxSavedInterruptStatus);
    if (xSwitchRequired != pdFALSE) {
        portYIELD_FROM_ISR();
    }
    return pdFALSE;  // enables yield in gptimer.c
}

// called from xTaskDelayUntil
void update_oneshot(TickType_t nextAlarm) {
    // nextAlarm is relative!!! => just set alarm

    // uint64_t a;
    // gptimer_get_raw_count(oneshotHandle,&a);
    // ESP_DRAM_LOGE("update1","current %lu, next: %lu, last: %lu, raw: %llu",currentAlarmTick,nextAlarm,lastAlarm,a);
    // ESP_DRAM_LOGE("update1-2","current %lu, next: %lu, last: %lu, raw: %llu",currentAlarmTick,nextAlarm,lastAlarm,a);

    if (currentAlarmTick <= nextAlarm) return;
    currentAlarmTick = nextAlarm;

    // gptimer_get_raw_count(oneshotHandle,&a);
    // ESP_DRAM_LOGE("update2","current %lu, next: %lu, last: %lu, raw: %llu",currentAlarmTick,nextAlarm,lastAlarm,a);

    gptimer_alarm_config_t alarm_config = {
        .reload_count = 0,
        .alarm_count = nextAlarm * 1000 * (1000 / CONFIG_FREERTOS_HZ),
        .flags.auto_reload_on_alarm = true,
    };
    gptimer_set_alarm_action(oneshotHandle, &alarm_config);

    // gptimer_alarm_config_t *alarm_config = (gptimer_alarm_config_t *)heap_caps_malloc(sizeof(gptimer_alarm_config_t), MALLOC_CAP_INTERNAL);
    // alarm_config->alarm_count = nextAlarm * 1000 * (1000 / CONFIG_FREERTOS_HZ);
    // ESP_ERROR_CHECK(gptimer_set_alarm_action(oneshotHandle, alarm_config));
    // heap_caps_free(alarm_config);
}

// called from xTickIncrement
void update_oneshotISR(TickType_t nextAlarm, TickType_t xTickCount) {
    // nextAlarm is absolute => just set alarm
    uint64_t a;
    gptimer_get_raw_count(oneshotHandle, &a);
    // ESP_DRAM_LOGE("updateISR1", "current %" PRIu32 ", next: %" PRIu32 ", last: %" PRIu32 ", raw: %" PRIu64, currentAlarmTick, nextAlarm, lastAlarm, a);

    lastAlarm = xTickCount;
    currentAlarmTick = nextAlarm;

    gptimer_get_raw_count(oneshotHandle, &a);
    // ESP_DRAM_LOGE("updateISR2", "current %" PRIu32 ", next: %" PRIu32 ", last: %" PRIu32 ", raw: %" PRIu64, currentAlarmTick, nextAlarm, lastAlarm, a);

    if (nextAlarm == portMAX_DELAY) {
        // ESP_DRAM_LOGE("updateISR","current %lu, next: %lu, last: %lu",currentAlarmTick,nextAlarm,lastAlarm);
        ESP_ERROR_CHECK(gptimer_set_alarm_action(oneshotHandle, NULL));  // disable alarm
        return;
    }

    gptimer_alarm_config_t alarm_config = {
        .reload_count = 0,
        .alarm_count = nextAlarm * 1000 * (1000 / CONFIG_FREERTOS_HZ),
        .flags.auto_reload_on_alarm = true,
    };
    ESP_ERROR_CHECK(gptimer_set_alarm_action(oneshotHandle, &alarm_config));
    // gptimer_alarm_config_t *alarm_config = (gptimer_alarm_config_t *)heap_caps_malloc(sizeof(gptimer_alarm_config_t), MALLOC_CAP_INTERNAL);
    // alarm_config->alarm_count = nextAlarm * 1000 * (1000 / CONFIG_FREERTOS_HZ);
    // ESP_ERROR_CHECK(gptimer_set_alarm_action(oneshotHandle, alarm_config));
    // heap_caps_free(alarm_config);
}

gptimer_handle_t IRAM_ATTR init_oneshot() {
    gptimer_handle_t gptimer = NULL;
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1 * 1000 * 1000,  // 1MHz, 1 tick = 1us
    };
    ESP_ERROR_CHECK(gptimer_new_timer(&timer_config, &gptimer));

    gptimer_alarm_config_t alarm_config = {
        .reload_count = 0,                                                    // counter will reload with 0 on alarm event
        .alarm_count = ONESHOT_INITIAL * 1000 * (1000 / CONFIG_FREERTOS_HZ),  // period = CONFIG_FREERTOS_HZ
        .flags.auto_reload_on_alarm = true,                                   // enable auto-reload
    };
    ESP_ERROR_CHECK(gptimer_set_alarm_action(gptimer, &alarm_config));

    ESP_DRAM_LOGI("timer init", "init oneshot to first alarm at %ld", ONESHOT_INITIAL);

    gptimer_event_callbacks_t cbs = {
        .on_alarm = timer_callback,  // register user callback
    };

    ESP_ERROR_CHECK(gptimer_register_event_callbacks(gptimer, &cbs, NULL));
    ESP_ERROR_CHECK(gptimer_enable(gptimer));
    return gptimer;
}

void start_oneshot() {
    ESP_ERROR_CHECK(gptimer_start(oneshotHandle));
    ESP_ERROR_CHECK(gptimer_set_raw_count(oneshotHandle, 0));
}

#endif

void app_main() {
    // disable all other interrupts
    for (int i = 0; i < XCHAL_NUM_INTERRUPTS; i++) {
        esp_intr_disable_source(i);
    }
    esp_timer_deinit();
    // enable only yield interrupt
    esp_intr_enable_source(ETS_FROM_CPU_INTR0_SOURCE_NO);

    if ((semOutput = xSemaphoreCreateBinary()) == NULL) {
        ESP_LOGE("app_main", "insufficient heap for semaphore");
        abort();
    }
#ifdef SYSTICK_DISABLED
    prepare_td();
#endif
#ifdef BENCH_TP_ISR_ALL
    // allocate timepoint arrays to external RAM
    tp_ccycles = (esp_cpu_cycle_count_t *)heap_caps_calloc(sizeof(esp_cpu_cycle_count_t), TP_LEN, MALLOC_CAP_SPIRAM);
    if (tp_ccycles == NULL) {
        ESP_LOGE("app_main", "Not enough memory for tp_ccycles array");
        abort();
    }
    for (size_t i = 0; i < TP_LEN; i++) tp_ccycles[i] = 0U;
#endif
#ifdef BENCH_INSERT
    // allocate timepoint arrays to external RAM
    insertion_times = (esp_cpu_cycle_count_t *)heap_caps_malloc(INSERT_LEN * sizeof(esp_cpu_cycle_count_t), MALLOC_CAP_SPIRAM);
    if (insertion_times == NULL) {
        ESP_LOGE("app_main", "Not enough memory for insertion_times array");
        abort();
    }
    for (size_t i = 0; i < INSERT_LEN; i++) insertion_times[i] = 0U;
    // allocate timepoint arrays to external RAM
    retrieval_times = (esp_cpu_cycle_count_t *)heap_caps_malloc(NUM_TICKS * sizeof(esp_cpu_cycle_count_t), MALLOC_CAP_SPIRAM);
    if (retrieval_times == NULL) {
        ESP_LOGE("app_main", "Not enough memory for retrieval_times array");
        abort();
    }
    for (size_t i = 0; i < NUM_TICKS; i++) retrieval_times[i] = 0U;
#endif
// #ifdef DEBUG
// debug
// tp_debug = (Debug_t *)heap_caps_calloc(sizeof(Debug_t), TP_LEN*100, MALLOC_CAP_SPIRAM);
// if (tp_debug == NULL) {
//     ESP_LOGE("app_main", "Not enough memory for tp_debug array");
//     abort();
// }
// for (size_t i = 0; i < TP_LEN; i++) tp_debug[i] = (Debug_t){.ccycle = -1U, .tick = -1U, .timer = -1U, .timerPeriod = -1U};
// #endif
#ifdef ENABLE_TASK_TRACE
    tp_tasks = (char **)heap_caps_malloc(TP_LEN * sizeof(char[16]), MALLOC_CAP_SPIRAM);
    if (tp_tasks == NULL) {
        ESP_LOGE("app_main", "Not enough memory for tp_tasks array");
        abort();
    }
    for (size_t i = 0; i < TP_LEN; i++) tp_tasks[i] = NULL;
#endif

    // IMPORTANT: MUST CREATE TASKS IN PRIORITY ORDER DESCENDING
    uint32_t taskNum = 0;
    printf("Start Task Description\n");

#if (DEADLINE_TEST == 1)
    int prio = number_of_tasks + 1;
#endif
    for (size_t i = 0; i < number_of_tasks; i++) {
#if (DEADLINE_TEST == 1)
        createTasks(&taskNum, 1, td[i].timer, td[i].period, TASK_STACK_SIZE, prio, dl_task, td[i].taskPos, td[i].executionTime);
        prio--;
#else
        createTasks(&taskNum, 1, td[i].timer, td[i].period, TASK_STACK_SIZE, TASK_PRIO, simple, td[i].taskPos);
#endif
    }
    printf("End Task Description\n");

    ESP_LOGI("createTask heap free", "num tasks %" PRIu32 ",total: %" PRIu32 ", overall min: %" PRIu32 ", block internal %zu, block PSRAM %zu", taskNum, esp_get_free_heap_size(), esp_get_minimum_free_heap_size(), heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL), heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM));

#ifdef SYSTICK_DISABLED
    // init only those timers that are required
    for (int i = 0; i < number_of_timers; i++) {
        timerHandles[i] = init_timer(i);
    }
#elif defined(ONESHOT)
    oneshotHandle = init_oneshot();
#endif
#ifdef ENERGY_TEST
    gpio_set_direction(GPIO_NUM_7, GPIO_MODE_OUTPUT);
    gpio_set_level(GPIO_NUM_7, 0);
#endif
    ESP_LOGI("app_main", "Starting scheduler from app_main()");
    vTaskStartScheduler();
    // this should never be reached
    ESP_LOGE("app_main", "insufficient RAM! aborting");
    abort();
}