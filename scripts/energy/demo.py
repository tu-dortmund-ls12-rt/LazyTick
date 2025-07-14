#!/usr/bin/env python3

import N6705C as adapter

import time


dev=adapter.N6705C()
dev.ch1_on()
time.sleep(5)
dev.ch0_on()

data_p1, data_c1, data_v1, data_p2, data_c2, data_v2, interval = dev.ch0_1_measure(interval=0.0001, mtime=15, curr_range=0.001)
# print(data_v)
#wait five seconds

dev.ch0_off()
dev.ch1_off()

dev.preview_double_channel_measure(data_p1, data_c1, data_v1, data_p2, data_c2, data_v2, interval)