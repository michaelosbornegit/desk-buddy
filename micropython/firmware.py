import requests
import os
import json

from secrets import device_secret, api_host
from utils import get_property_if_exists

versions_file = 'versions.json'
versions = {}

try:
    with open(versions_file, 'r') as f:
        versions = json.load(f)
except OSError:
    versions = {}
    with open(versions_file, 'w') as f:
        json.dump(versions, f)

def makedirs(path):
    """Recursively create directories, handling paths without os.path."""
    # Normalize the path and remove the file part if present
    path = '/'.join(path.split('/')[:-1])  # Remove the last component (file name)
    if path == '/':
        return  # If the path becomes empty, nothing to do

    # Split the path into components and create directories
    parts = path.split('/')
    current_path = "/"
    
    for part in parts:
        current_path += f"{part}"
        try:
            os.mkdir(current_path)
        except OSError as e:
            # Ignore error if directory already exists
            if e.args[0] != 17:  # 17 is 'EEXIST' error code
                raise
        current_path += "/"

def _check_for_update(firmware):
    global versions
    relative_path = firmware['relative_path']
    current_device_version = 0
    update_available = False

    current_device_version = get_property_if_exists(versions, relative_path, 0)
    if firmware['version'] > current_device_version:
    # for debugging, always upload all files
    # if True:
        update_available = True
    
    return update_available

def firmware_check(device_config):
    global versions
    with open(versions_file, 'r') as f:
        versions = json.load(f)
    # Check if we need to update firmware
    for firmware in device_config['firmware']:
        return _check_for_update(firmware)


def firmware_update(device_config):
    global versions
    with open(versions_file, 'r') as f:
        versions = json.load(f)
    versions_modified = False

    for firmware in device_config['firmware']:
        update_available = _check_for_update(firmware)
        # don't allow writing important micropython firmware files
        if firmware['relative_path'] in ['boot.py', 'main.py', 'secrets.py']:
            raise Exception(f'Firmware updater tried something forbidden: overwriting {firmware["relative_path"]}')
        if update_available:
            # quote periods
            encoded_relative_path = firmware['relative_path'].replace('.', '%2E')
            # We need to make up our own encoding because the normal doesn't work with flask
            encoded_relative_path = encoded_relative_path.replace('/', '^$#')
            firmware_response = requests.get(f'{api_host}/devices/firmware/{encoded_relative_path}', headers={'Authorization': device_secret})
            
            # Ensure directories exist before opening the file
            makedirs(firmware['relative_path'])
            
            # Write the file
            with open(firmware['relative_path'], 'wb') as f:
                print(f'Writing firmware to {firmware["relative_path"]}')
                f.write(firmware_response.content)
                versions[firmware['relative_path']] = firmware['version']
                versions_modified = True
    
    if versions_modified:
        with open(versions_file, 'w') as f:
            json.dump(versions, f)