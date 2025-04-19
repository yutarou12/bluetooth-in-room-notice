import asyncio
import yaml
from bleak import BleakScanner
from charset_normalizer import detect

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

async def scan_for_devices():
    devices = await BleakScanner.discover(return_adv=True)
    ids_yaml = load_config('./public/assigned_numbers/company_identifiers/company_identifiers.yaml')
    # print(ids_yaml['company_identifiers'])
    sum = 0
    for k, v in devices.items():
        print(f"device: {k}")
        print(f"- rssi: {v[1].rssi}")
        result = list(v[1].manufacturer_data.keys())[0]
        print(f"- id: {str(hex(result))}")
        # print(str(hex(result)).replace("0x", "0x"+"0"*(6 - len(str(hex(result)))) ))
        for c in ids_yaml['company_identifiers']:
            if c['value'] == result:
                print(f"- company: {str(c['name'])}")
                break
        sum += 1
    print(f"All {sum} ")
loop = asyncio.new_event_loop()
loop.run_until_complete(scan_for_devices())
