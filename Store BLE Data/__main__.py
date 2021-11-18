import os
import keyboard
from multiprocessing import Pool
# https://medium.com/@leportella/how-to-run-parallel-processes-8939dafae81e

# List all the scripts that shall be run
processes = ('print_BLE_characteristics_CSV_1.py', 'print_BLE_characteristics_CSV_2.py')

# Adapt number of processes
numProcesses = len(processes)

def run_process(process):
    os.system('python {}'.format(process))


if __name__ == '__main__':

    pool = Pool(processes=numProcesses)
    pool.map(run_process, processes)
    if keyboard.is_pressed('q'):  # if key 'q' is pressed
        print('You Pressed A Key!')
