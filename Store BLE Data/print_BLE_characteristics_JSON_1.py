import asyncio
import platform
import sys
import time
import json
import os
from datetime import datetime
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
        filename = "data_{}.json".format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime()))
        arduino_data_file = open(path + "/" + filename, 'w')

        # access BLE Data and write to CSV file
        while True:

            # BLE data from peripheral are the sensor values as a string
            ble_IMU = await client.read_gatt_char(ble_IMU_UUID)

            s_ble_IMU = "{0}".format("".join(map(chr, ble_IMU)))

            # split sensor string consisting of 3 different values into list elements
            s_ble_IMU_split = s_ble_IMU.split(",")

            # timestamp for sensor values
            unix_time = datetime.utcnow().strftime('%Y_%m_%d_%H:%M:%S.%f')[:-3]

            # define json database structure
            json_data = {
                "timestamp:": unix_time,
                "PT_1_Acc_X": float(s_ble_IMU_split[0]),
                "PT_1_Acc_Y": float(s_ble_IMU_split[1]),
                "PT_1_Acc_Z": float(s_ble_IMU_split[2]),

                "PT_1_Gyro_X": float(s_ble_IMU_split[3]),
                "PT_1_Gyro_Y": float(s_ble_IMU_split[4]),
                "PT_1_Gyro_Z": float(s_ble_IMU_split[5]),

                "PT_1_Magn_X": float(s_ble_IMU_split[6]),
                "PT_1_Magn_Y": float(s_ble_IMU_split[7]),
                "PT_1_Magn_Z": float(s_ble_IMU_split[8]),
            }

            json_data = json.dumps(json_data)
            print(json_data)

            # Store data into JSON file
            arduino_data_file.write("%s\n" % json_data)

        arduino_data_file.close()

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address_1, ble_IMU_UUID_1, index_1))
