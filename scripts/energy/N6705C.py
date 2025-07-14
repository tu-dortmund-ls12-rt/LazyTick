#!/usr/bin/env python3

import pyvisa
import datetime
import time

import numpy as np
import matplotlib.pyplot as plt


class N6705C:

    instrument = None

    def __init__(self):
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource("TCPIP::129.217.34.156::5025::SOCKET")
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
        print(self.instrument.query("*IDN?"))

    def ch0_off(self):
        self.instrument.write("OUTP OFF, (@1)")

    def ch0_on(self):
        self.instrument.write("OUTP ON, (@1)")

    def ch1_off(self):
        self.instrument.write("OUTP OFF, (@2)")

    def ch1_on(self):
        self.instrument.write("OUTP ON, (@2)")

    def ch0_measure(self, interval=0.001, mtime=10, curr_range=0.01, volr_range=5):
        # self.instrument.write("FORM REAL")
        self.instrument.write("FORM ASCII")
        print("Measure format set to "+self.instrument.query("FORM?"))
        self.instrument.write("SENS:SWE:TINT " + str(interval)+", (@1)")
        set_interval = self.instrument.query("SENS:SWE:TINT? (@1)")
        print("Measure timesteps set to "+set_interval)
        npoints = int(mtime/float(set_interval))
        self.instrument.write("SENS:SWE:POIN " + str(npoints)+", (@1)")
        print("Measure samples set to "+self.instrument.query("SENS:SWE:POIN? (@1)"))
        self.instrument.write("SENS:CURR:RANG " + str(curr_range)+", (@1)")
        print("Measure current range set to "+self.instrument.query("SENS:CURR:RANG? (@1)"))
        self.instrument.write("SENS:VOLT:RANG " + str(volr_range)+", (@1)")
        print("Measure voltage range set to "+self.instrument.query("SENS:VOLT:RANG? (@1)"))

        a_mres_power = self.instrument.query("MEAS:ARR:POW? (@1)", delay=mtime)
        a_mres_current = self.instrument.query("FETC:ARR:CURR? (@1)")
        a_mres_voltage = self.instrument.query("FETC:ARR:VOLT? (@1)")
        res_arr = a_mres_power.split(",")
        mres_power = []
        for res in res_arr:
            mres_power.append(float(res))

        res_arr = a_mres_current.split(",")
        mres_current = []
        for res in res_arr:
            mres_current.append(float(res))

        res_arr = a_mres_voltage.split(",")
        mres_voltage = []
        for res in res_arr:
            mres_voltage.append(float(res))

        # mres_power=self.instrument.query_binary_values("MEAS:ARR:POW? (@1)", datatype='f', delay=mtime)
        # mres_current=self.instrument.query_binary_values("FETC:ARR:CURR? (@1)", datatype='f')
        # mres_voltage=self.instrument.query_binary_values("FETC:ARR:VOLT? (@1)", datatype='f')
        return (mres_power, mres_current, mres_voltage, float(set_interval))

    def ch0_1_measure(self, interval=0.001, mtime=10, curr_range=0.01, volr_range=5):
        # self.instrument.write("FORM REAL")
        self.instrument.write("FORM ASCII")
        print("Measure format set to "+self.instrument.query("FORM?"))
        self.instrument.write("SENS:SWE:TINT " + str(interval)+", (@1)")
        self.instrument.write("SENS:SWE:TINT " + str(interval)+", (@2)")
        set_interval = self.instrument.query("SENS:SWE:TINT? (@1)")
        print("Measure timesteps for Ch 0 set to "+set_interval)
        set_interval = self.instrument.query("SENS:SWE:TINT? (@2)")
        print("Measure timesteps for Ch 1 set to "+set_interval)
        npoints = int(mtime/float(set_interval))
        self.instrument.write("SENS:SWE:POIN " + str(npoints)+", (@1)")
        print("Measure samples Ch 0 set to "+self.instrument.query("SENS:SWE:POIN? (@1)"))
        self.instrument.write("SENS:SWE:POIN " + str(npoints)+", (@2)")
        print("Measure samples Ch 1 set to "+self.instrument.query("SENS:SWE:POIN? (@2)"))
        self.instrument.write("SENS:CURR:RANG " + str(curr_range)+", (@1)")
        print("Measure current range Ch 0 set to "+self.instrument.query("SENS:CURR:RANG? (@1)"))
        self.instrument.write("SENS:CURR:RANG " + str(curr_range)+", (@2)")
        print("Measure current range Ch 1 set to "+self.instrument.query("SENS:CURR:RANG? (@2)"))
        self.instrument.write("SENS:VOLT:RANG " + str(volr_range)+", (@1)")
        print("Measure voltage range Ch 0 set to "+self.instrument.query("SENS:VOLT:RANG? (@1)"))
        self.instrument.write("SENS:VOLT:RANG " + str(volr_range)+", (@2)")
        print("Measure voltage range Ch 1 set to "+self.instrument.query("SENS:VOLT:RANG? (@2)"))

        print("Starting Measuremen")

        a_mres_power = self.instrument.query("MEAS:ARR:POW? (@1,2)", delay=mtime)

        print("Stopping Measurement")
        print("Fetching Results")

        ch_0_a_mres_power = self.instrument.query("FETC:ARR:POW? (@1)")
        ch_0_a_mres_current = self.instrument.query("FETC:ARR:CURR? (@1)")
        ch_0_a_mres_voltage = self.instrument.query("FETC:ARR:VOLT? (@1)")
        ch_1_a_mres_power = self.instrument.query("FETC:ARR:POW? (@2)")
        ch_1_a_mres_current = self.instrument.query("FETC:ARR:CURR? (@2)")
        ch_1_a_mres_voltage = self.instrument.query("FETC:ARR:VOLT? (@2)")

        print("Results fetched, parsing...")

        ch_0_res_arr = ch_0_a_mres_power.split(",")
        ch_0_mres_power = []
        for res in ch_0_res_arr:
            ch_0_mres_power.append(float(res))

        ch_0_res_arr = ch_0_a_mres_current.split(",")
        ch_0_mres_current = []
        for res in ch_0_res_arr:
            ch_0_mres_current.append(float(res))
        ch_0_res_arr = ch_0_a_mres_voltage.split(",")
        ch_0_mres_voltage = []
        for res in ch_0_res_arr:
            ch_0_mres_voltage.append(float(res))

        ch1_res_arr = ch_1_a_mres_power.split(",")
        ch1_mres_power = []
        for res in ch1_res_arr:
            ch1_mres_power.append(float(res))

        ch1_res_arr = ch_1_a_mres_current.split(",")
        ch1_mres_current = []
        for res in ch1_res_arr:
            ch1_mres_current.append(float(res))
        ch1_res_arr = ch_1_a_mres_voltage.split(",")
        ch1_mres_voltage = []
        for res in ch1_res_arr:
            ch1_mres_voltage.append(float(res))

        return (ch_0_mres_power, ch_0_mres_current, ch_0_mres_voltage, ch1_mres_power, ch1_mres_current, ch1_mres_voltage, float(set_interval))

    def preview_measure(self, data_p, data_c, data_v, interval):
        fig, axs = plt.subplots(3)
        fig.suptitle("Measurement Results (preview), TOTAL "+str(sum(data_p)*interval)+" Wh [J]")
        axs[0].plot(np.multiply(range(0, len(data_p)), interval), data_p)
        axs[0].set_title("Power Consumption (AVG: "+str(sum(data_p)/len(data_p))+") [W]")
        axs[0].set_ylim([0, max(data_p)*1.1])
        axs[1].plot(np.multiply(range(0, len(data_v)), interval), data_v)
        axs[1].set_title("Voltage (AVG: "+str(sum(data_v)/len(data_v))+") [V]")
        axs[1].set_ylim([0, max(data_v)*1.1])
        axs[2].plot(np.multiply(range(0, len(data_c)), interval), data_c)
        axs[2].set_title("Current (AVG: "+str(sum(data_c)/len(data_c))+") [A]")
        axs[2].set_ylim([0, max(data_c)*1.1])

        plt.xlabel("time [s]")
        plt.show()

    def preview_double_channel_measure(self, data_p1, data_c1, data_v1, data_p2, data_c2, data_v2, interval):
        active_time = [i for i, d in enumerate(data_v2) if d > 3]
        end_active = max(active_time)
        zero_time = [i for i, d in enumerate(data_v2) if d < 0.1 and i < end_active]
        end_zero = max(zero_time[:end_active])
        measurement_start = end_zero + 1
        measurement_end = end_active + 1
        data_p1 = data_p1[measurement_start:measurement_end]
        data_c1 = data_c1[measurement_start:measurement_end]
        data_v1 = data_v1[measurement_start:measurement_end]
        data_p2 = data_p2[measurement_start:measurement_end]
        data_c2 = data_c2[measurement_start:measurement_end]
        data_v2 = data_v2[measurement_start:measurement_end]

        # write data to csv file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"{timestamp}-meas.csv", "w") as f:
            f.write("Time [s], Power Ch 1 [W], Voltage Ch 1 [V], Current Ch 1 [A], Power Ch 2 [W], Voltage Ch 2 [V], Current Ch 2 [A]\n")
            for i in range(len(data_p1)):
                f.write(f"{i * interval}, {data_p1[i]}, {data_v1[i]}, {data_c1[i]}, {data_p2[i]}, {data_v2[i]}, {data_c2[i]}\n")
        print("Measurement results written to meas.csv")

        fig, axs = plt.subplots(6)
        fig.suptitle("Measurement Results (preview), TOTAL "+str(sum(data_p1)*interval)+" Ws [J]")
        axs[0].plot(np.multiply(range(0, len(data_p1)), interval), data_p1)
        axs[0].set_title("Power Consumption (AVG: "+str(sum(data_p1)/len(data_p1))+") [W]")
        # axs[0].set_ylim([0, max(data_p1)*1.1])
        axs[0].set_ylim([0, 0.35])
        axs[1].plot(np.multiply(range(0, len(data_v1)), interval), data_v1)
        axs[1].set_title("Voltage (AVG: "+str(sum(data_v1)/len(data_v1))+") [V]")
        axs[1].set_ylim([0, max(data_v1)*1.1])
        axs[2].plot(np.multiply(range(0, len(data_c1)), interval), data_c1)
        axs[2].set_title("Current (AVG: "+str(sum(data_c1)/len(data_c1))+") [A]")
        axs[2].set_ylim([0, max(data_c1)*1.1])

        axs[3].plot(np.multiply(range(0, len(data_p2)), interval), data_p2)
        axs[3].set_title("Power Consumption Ch 2 (AVG: "+str(sum(data_p2)/len(data_p2))+") [W]")
        axs[3].set_ylim([0, max(data_p2)*1.1])
        axs[4].plot(np.multiply(range(0, len(data_v2)), interval), data_v2)
        axs[4].set_title("Voltage Ch 2 (AVG: "+str(sum(data_v2)/len(data_v2))+") [V]")
        axs[4].set_ylim([0, max(data_v2)*1.1])
        axs[5].plot(np.multiply(range(0, len(data_c2)), interval), data_c2)
        axs[5].set_title("Current Ch 2 (AVG: "+str(sum(data_c2)/len(data_c2))+") [A]")
        axs[5].set_ylim([0, max(data_c2)*1.1])

        plt.xlabel("time [s]")

        # save figure as vector graphic pdf
        fig.savefig(f"{timestamp}-meas.pdf", format='pdf', bbox_inches='tight')
        print("Measurement results saved to meas.pdf")

        plt.show()