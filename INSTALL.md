# Install
Whether the software and hardware environment is correctly setup can be check by running:
1. `. ./esp-idf/export.sh` from the root of the repository to activate the `idf.py` commands.
2. `idf.py build flash` to build and flash the firmware to the ESP32.
3. `idf.py monitor` to display the UART output of the experiment run.
4. When an experiment run has finished without errors, the last displayed line should look like: `I output_retr: RETRIEVAL OUTPUT END` when running experiments for figures 7.5, 7.6, 7.7 or `I output: INTERRUPT OUTPUT END` when running the deadline miss experiments for figure 7.8.