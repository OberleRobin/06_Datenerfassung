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

address_2 = (
    "94:ca:a5:a0:ea:4b"
    if platform.system() != "Darwin"
    else "61691946-1A55-4323-9FB2-8539D878FB44"
)
# UUID of characteristics Defined in Arduino Code
ble_IMU_UUID_2 = "4ae507ce-530a-4c8b-9aa9-7f3424698d74"
index_2 = 2

if len(sys.argv) == 2:
    address_1 = sys.argv[1]
    address_2 = sys.argv[1]

async def run(address, ble_IMU_UUID, index):

    device_1 = await BleakScanner.find_device_by_address(address_1, timeout=20.0)
    if not device_1:
        raise BleakError(f"A device with address {address_1} could not be found.")
    client_1 = BleakClient(device_1)

    device_2 = await BleakScanner.find_device_by_address(address_2, timeout=20.0)
    if not device_2:
        raise BleakError(f"A device with address {address_2} could not be found.")
    client_2 = BleakClient(device_2)

    try:
        await client_1.connect()
        await client_2.connect()

        # detect the current working directory and print it
        path = os.getcwd()
        new_path = path + "/" + time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())

        try:
            os.mkdir(new_path)
        except OSError:
            print("Creation of the directory %s failed" % new_path)

        filename_1 = "data_{}.json".format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
                                           + '_Device' + str(index_1))
        arduino_data_file_1 = open(new_path + "/" + filename_1, 'w')

        filename_2 = "data_{}.json".format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
                                           + '_Device' + str(index_2))
        arduino_data_file_2 = open(new_path + "/" + filename_2, 'w')

        # access BLE Data and write to CSV file
        while True:

            # BLE data from peripheral are the sensor values as a string
            ble_IMU_1 = await client_1.read_gatt_char(ble_IMU_UUID_1)
            ble_IMU_2 = await client_2.read_gatt_char(ble_IMU_UUID_2)

            s_ble_IMU_1 = "{0}".format("".join(map(chr, ble_IMU_1)))
            s_ble_IMU_2 = "{0}".format("".join(map(chr, ble_IMU_2)))

            # split sensor string consisting of 3 different values into list elements
            s_ble_IMU_split_1 = s_ble_IMU_1.split(",")
            s_ble_IMU_split_2 = s_ble_IMU_2.split(",")

            # timestamp for sensor values
            unix_time = datetime.utcnow().strftime('%Y_%m_%d_%H:%M:%S.%f')[:-3]

            # define json database structure

            json_data_1 = {
                "timestamp:": unix_time,
                "PT_1_Acc_X": float(s_ble_IMU_split_1[0]),
                "PT_1_Acc_Y": float(s_ble_IMU_split_1[1]),
                "PT_1_Acc_Z": float(s_ble_IMU_split_1[2]),

                "PT_1_Gyro_X": float(s_ble_IMU_split_1[3]),
                "PT_1_Gyro_Y": float(s_ble_IMU_split_1[4]),
                "PT_1_Gyro_Z": float(s_ble_IMU_split_1[5]),

                "PT_1_Magn_X": float(s_ble_IMU_split_1[6]),
                "PT_1_Magn_Y": float(s_ble_IMU_split_1[7]),
                "PT_1_Magn_Z": float(s_ble_IMU_split_1[8]),
            }

            json_data_2 = {
                "timestamp:": unix_time,
                "PT_2_Acc_X": float(s_ble_IMU_split_2[0]),
                "PT_2_Acc_Y": float(s_ble_IMU_split_2[1]),
                "PT_2_Acc_Z": float(s_ble_IMU_split_2[2]),

                "PT_2_Gyro_X": float(s_ble_IMU_split_2[3]),
                "PT_2_Gyro_Y": float(s_ble_IMU_split_2[4]),
                "PT_2_Gyro_Z": float(s_ble_IMU_split_2[5]),

                "PT_2_Magn_X": float(s_ble_IMU_split_2[6]),
                "PT_2_Magn_Y": float(s_ble_IMU_split_2[7]),
                "PT_2_Magn_Z": float(s_ble_IMU_split_2[8]),
            }

            json_data_1 = json.dumps(json_data_1)
            json_data_2 = json.dumps(json_data_2)
            print(json_data_1)
            print(json_data_2)

            # Store data into JSON file
            arduino_data_file_1.write("%s\n" % json_data_1)
            arduino_data_file_2.write("%s\n" % json_data_2)

        arduino_data_file_1.close()
        arduino_data_file_2.close()

    except Exception as e:
        print(e)
    finally:
        await client_1.disconnect()
        await client_2.disconnect()

# if __name__ == 'print_BLE_characteristics_2':
loop = asyncio.get_event_loop()
# loop.run_until_complete(run(address_1, ble_IMU_UUID_1, index1))
loop.run_until_complete(run(address_2, ble_IMU_UUID_2, index_2))
