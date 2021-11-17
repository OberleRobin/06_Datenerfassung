import asyncio
import platform
import sys
import time
from datetime import datetime
import json
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

address = (
    "9a:04:76:6c:6d:45"
    if platform.system() != "Darwin"
    else "DC401059-F9B9-463E-B8DF-CF5FE739B921"
)
if len(sys.argv) == 2:
    address = sys.argv[1]

ble_acceleration_UUID = "6c1da4e1-ded2-4e1b-8e1c-2a336be87422"
ble_magnetic_UUID = "2ad3134f-bbc8-4e00-aca2-119415b3d1f8"
ble_gyroscope_UUID = "474cb28a-468b-4f73-87f7-a9a5d39e65eb"

async def run(address):
    device = await BleakScanner.find_device_by_address(address, timeout=20.0)
    if not device:
        raise BleakError(f"A device with address {address} could not be found.")
    client = BleakClient(device)
    try:
        await client.connect()

        filename = "data_{}.json".format(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime()))
        arduinoDataFile = open(filename, 'w')

        # access BLE Data and write to CSV file
        while True:

            ble_acceleration = await client.read_gatt_char(ble_acceleration_UUID)
            ble_magnetic = await client.read_gatt_char(ble_magnetic_UUID)
            ble_gyroscope = await client.read_gatt_char(ble_gyroscope_UUID)

            s_ble_acceleration = "{0}".format("".join(map(chr, ble_acceleration)))
            s_ble_magnetic = "{0}".format("".join(map(chr, ble_magnetic)))
            s_ble_gyroscope = "{0}".format("".join(map(chr, ble_gyroscope)))

            # print(s_ble_acceleration)
            # print(s_ble_magnetic)
            # print(s_ble_gyroscope)

            s_ble_acceleration_split = s_ble_acceleration.split(",")
            s_ble_magnetic_split = s_ble_magnetic.split(",")
            s_ble_gyroscope_split = s_ble_gyroscope.split(",")

            unixTime = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]

            json_data = {
                "timestamp:": unixTime,
                "PhysioTex_1": [[float(s_ble_acceleration_split[0])],
                                [float(s_ble_acceleration_split[1])],
                                [float(s_ble_acceleration_split[2])],

                                [float(s_ble_magnetic_split[0])],
                                [float(s_ble_magnetic_split[1])],
                                [float(s_ble_magnetic_split[2])],

                                [float(s_ble_gyroscope_split[0])],
                                [float(s_ble_gyroscope_split[1])],
                                [float(s_ble_gyroscope_split[2])]]
            }
            print(json_data)
            arduinoDataFile.write("%s\n" % json_data)

        arduinoDataFile.close()

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))