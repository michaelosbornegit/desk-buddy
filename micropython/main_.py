from machine import Pin
import time
import network
import requests
import esp32
import sys
import mip

from display.enh_display import Enhanced_Display
from secrets import ssid, ssid_password, device_secret, api_host, device_id
from osb_firmware import firmware_update

DISPLAY = Enhanced_Display(bus=0, sda=Pin(6), scl=Pin(7))
NVS_NAMESPACE = 'storage'
nvs = esp32.NVS(NVS_NAMESPACE)

def connectToNetwork():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f'Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, ssid_password)
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ipconfig('addr4'))

def register():
    response = requests.post(f'{api_host}/devices/register', headers={'Authorization': device_secret},
                             json={'deviceId': device_id, 'username': 'test', 'password': 'test'})

    if response.status_code == 200:
        print('Registered successfully')
    else:
        raise Exception(f'Error registering: {response.status_code}')

    return response.json()

def main():
    while True:
        try:
            connectToNetwork()

            # Install necessary modules
            mip.install('copy')

            device_config = register()

            # Update firmware on boot
            firmware_update(device_config)

            # Import executor safely
            if 'executor' in sys.modules:
                del sys.modules['executor']
            __import__('executor')
            break
        except KeyError as e:
            print(f"KeyError: {e} - Check if 'executor.py' exists and is properly named.")
        except Exception as e:
            DISPLAY.clear()
            DISPLAY.text("Desk Buddy", 0, 0, 1, 0, 128, 64, 1)
            DISPLAY.text("encountered an", 0, 8, 1, 0, 128, 64, 1)
            DISPLAY.text("irrecoverable", 0, 16, 1, 0, 128, 64, 1)
            DISPLAY.text("error", 0, 24, 1, 0, 128, 64, 1)
            DISPLAY.text("x.x", 0, 40, 1, 0, 128, 64, 1)
            DISPLAY.text("Restarting...", 0, 56, 1, 0, 128, 64, 1)
            DISPLAY.show()
            sys.print_exception(e)
            print('irrecoverable error, restarting...')
            time.sleep(5)


main()