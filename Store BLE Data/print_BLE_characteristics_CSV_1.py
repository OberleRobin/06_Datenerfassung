import asyncio
import platform
import sys
import time
import csv
import os
import keyboard
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# For Apple Mac's, only UUID can be used
# Windows and Linux us MAC-Address
address_1 = (
    "9a:04:76:6c:6d:45"
    if platform.system() != "Darwin"
    else "DC401059-F9B9-463E-B8DF-CF5FE739B921"
)
# UUID of characteristics Defined in Arduino Code
ble_IMU_UUID_1 = "6c1da4e1-ded2-4e1b-8e1c-2a336be87422"
index_1 = 1

if len(sys.argv) == 2:
    address_2 = sys.argv[1]

async def run(address, ble_IMU_UUID, index):
    device = await BleakScanner.find_device_by_address(address, timeout=20.0)
    if not device:
        raise BleakError(f"A device with address {address} could not be found.")
    client = BleakClient(device)

    try:
        await client.connect()

        # define directory for data storage
        path = os.getcwd() + "/" + 'device' + str(index)

        # create new file for each sample
        filename = "data_{}.csv".format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime()))
        arduino_data_file = open(path + "/" + filename, 'w')

        # write header into CSV file
        fieldnames = ['timestamp', 'Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz']

        # adds whitespace behind sensorvalues
        writer = csv.DictWriter(arduino_data_file, fieldnames=fieldnames,
                                escapechar=' ', quoting=csv.QUOTE_NONE)
        writer.writeheader()

        # access BLE Data and write to CSV file
        while True:

            # BLE data from peripheral are the sensor values as a string
            ble_IMU = await client.read_gatt_char(ble_IMU_UUID)
            s_ble_IMU = "{0}".format("".join(map(chr, ble_IMU)))

            # timestamp for sensor values
            unix_time = round(time.time() * 1000)

            # write data with timestamp into CSV file
            writer.writerow({'timestamp': unix_time, 'Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz': s_ble_IMU})

            print("Device 1: ", unix_time, ": " + s_ble_IMU)

            # if keyboard.is_pressed('q'):  # if key 'q' is pressed
            #     print('You Pressed A Key!')
            #     break  # finishing the loop

        arduino_data_file.close()

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address_1, ble_IMU_UUID_1, index_1))
