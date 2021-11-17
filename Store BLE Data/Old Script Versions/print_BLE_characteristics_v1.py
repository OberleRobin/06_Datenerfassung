import asyncio
import platform
import sys
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
        # access BLE Data
        while True:

            ble_acceleration = await client.read_gatt_char(ble_acceleration_UUID)
            ble_magnetic = await client.read_gatt_char(ble_magnetic_UUID)
            ble_gyroscope = await client.read_gatt_char(ble_gyroscope_UUID)

            print("Acceleration: {0}".format("".join(map(chr, ble_acceleration))))
            print("Magnetometer: {0}".format("".join(map(chr, ble_magnetic))))
            print("Gyroscope: {0}".format("".join(map(chr, ble_gyroscope))))

    except Exception as e:
        print(e)
    finally:
        await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))