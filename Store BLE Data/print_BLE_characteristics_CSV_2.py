import asyncio
import platform
import sys
import time
import csv
import os
from datetime import datetime
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# For Apple Mac's, only UUID can be used
# Windows and Linux us MAC-Address
address_2 = (
    "94:ca:a5:a0:ea:4b"
    if platform.system() != "Darwin"
    else "61691946-1A55-4323-9FB2-8539D878FB44"
)
# UUID of characteristics Defined in Arduino Code
ble_IMU_UUID_2 = "4ae507ce-530a-4c8b-9aa9-7f3424698d74"
index_2 = 2

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
            unix_time = datetime.utcnow().strftime('%Y_%m_%d_%H:%M:%S.%f')[:-3]

            # write data with timestamp into CSV file
            writer.writerow({'timestamp': unix_time, 'Ax,Ay,Az,Gx,Gy,Gz,Mx,My,Mz': s_ble_IMU})

            print("Device 2: " + unix_time + ": " + s_ble_IMU)

        arduino_data_file.close()

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address_2, ble_IMU_UUID_2, index_2))
