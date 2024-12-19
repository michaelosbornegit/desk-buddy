import esp32
import requests

from secrets import device_secret, api_host

NVS_NAMESPACE = 'storage'
nvs = esp32.NVS(NVS_NAMESPACE)

def _check_for_update(firmware):
    file_name = firmware['file_name']
    currentDeviceVersion = 0
    update_available = False
    try:
        currentDeviceVersion = nvs.get_i32(file_name)
        if firmware['version'] > currentDeviceVersion:
            update_available = True
    except OSError: # key doesn't exist
        update_available = True
    
    return update_available

def firmware_check(device_config):
    # Check if we need to update firmware
    for firmware in device_config['firmware']:
        update_available = _check_for_update(firmware)
        if update_available:
            return True

def firmware_update(device_config):
    nvs_modified = False

    for firmware in device_config['firmware']:
        update_available = _check_for_update(firmware)
        # don't allow writing important micropython firmware files
        if firmware['file_name'] in ['boot.py', 'main.py', 'firmware.py', 'secrets.py']:
            raise Exception(f'Firmware updater tried something forbidden: overwriting {firmware["file_name"]}')
        if update_available:
            firmware_response = requests.get(f'{api_host}/devices/firmware/{firmware['file_name']}', headers={'Authorization': device_secret})
            with open(firmware['relative_path'], 'wb') as f:
                print(f'Writing firmware to {firmware["relative_path"]}')
                f.write(firmware_response.content)
                nvs.set_i32(firmware['file_name'], firmware['version'])
                nvs_modified = True
    
    if nvs_modified:
        nvs.commit()