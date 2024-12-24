from machine import Pin
import time
import network
import requests
import esp32
import sys
import mip
import machine
import os
import asyncio

from display.enh_display import Enhanced_Display
from secrets import device_secret, api_host, device_id
from osb_firmware import firmware_update
from hwconfig import DISPLAY, BUTTON

NVS_NAMESPACE = 'storage'
nvs = esp32.NVS(NVS_NAMESPACE)

def connectToNetwork(ssid, ssid_password):
    DISPLAY.clear()
    DISPLAY.text("Connecting to", 0, 0, 1, 0, 128, 64, 1)
    DISPLAY.text(f"{ssid}", 0, 16, 1, 0, 128, 64, 1)
    DISPLAY.text("((i))", 0, 32, 1, 0, 128, 64, 1)
    DISPLAY.text("|", 0, 40, 1, 0, 128, 64, 1)
    DISPLAY.text("[o_o]", 0, 48, 1, 0, 128, 64, 1)
    DISPLAY.show()
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
    button_held_time = 0
    while not BUTTON.value():
        DISPLAY.clear()
        DISPLAY.text("Keep holding to", 0, 0, 1, 0, 128, 64, 1)
        DISPLAY.text("factory reset me...", 0, 16, 1, 0, 128, 64, 1)
        DISPLAY.text("i", 0, 32, 1, 0, 128, 64, 1)
        DISPLAY.text("|", 0, 40, 1, 0, 128, 64, 1)
        DISPLAY.text("[o_o]", 0, 48, 1, 0, 128, 64, 1)
        DISPLAY.show()
        button_held_time += 1
        time.sleep(0.01)
        if button_held_time == 100:
            DISPLAY.clear()
            DISPLAY.text("Factory reset", 0, 0, 1, 0, 128, 64, 1)
            DISPLAY.text("in progress...", 0, 16, 1, 0, 128, 64, 1)
            DISPLAY.text("i", 0, 32, 1, 0, 128, 64, 1)
            DISPLAY.text("|", 0, 40, 1, 0, 128, 64, 1)
            DISPLAY.text("[x_x]", 0, 48, 1, 0, 128, 64, 1)
            DISPLAY.show()
            time.sleep(2)
            p = esp32.Partition.find(esp32.Partition.TYPE_DATA, label='nvs')[0]

            # p.info()[3] is partition size
            for x in range(int(p.info()[3] / 4096)):
                p.writeblocks(x, bytearray(4096))
            
            try:
                os.remove('wifi_config.py')
            except OSError:
                pass

            machine.reset()
    DISPLAY.clear()
    DISPLAY.text("Desk Buddy is", 0, 0, 1, 0, 128, 64, 1)
    DISPLAY.text("Starting up...", 0, 16, 1, 0, 128, 64, 1)
    DISPLAY.text("i", 0, 32, 1, 0, 128, 64, 1)
    DISPLAY.text("|", 0, 40, 1, 0, 128, 64, 1)
    DISPLAY.text("[o_o]", 0, 48, 1, 0, 128, 64, 1)
    DISPLAY.show()
    time.sleep(3)
    while True:
        try:
            try:
                import wifi_config
                ssid = wifi_config.ssid
                ssid_password = wifi_config.ssid_password
            except ImportError:
                import captive_portal_setup
                captive_portal_setup.main()
                break
            
            connectToNetwork()

            # Install necessary modules
            mip.install('copy')

            device_config = register()

            # Update firmware on boot
            firmware_update(device_config)

            # Import executor safely
            import executor
            asyncio.run(main())
            break
        except KeyError as e:
            print(f"KeyError: {e} - Check if 'executor.py' exists and is properly named.")
        except Exception as e:
            DISPLAY.clear()
            DISPLAY.text("Desk Buddy", 0, 0, 1, 0, 128, 64, 1)
            DISPLAY.text("encountered an", 0, 8, 1, 0, 128, 64, 1)
            DISPLAY.text("irrecoverable", 0, 16, 1, 0, 128, 64, 1)
            DISPLAY.text("error", 0, 24, 1, 0, 128, 64, 1)
            DISPLAY.text("[x.x]", 0, 40, 1, 0, 128, 64, 1)
            DISPLAY.text("Restarting...", 0, 56, 1, 0, 128, 64, 1)
            DISPLAY.show()
            sys.print_exception(e)
            print('irrecoverable error, restarting...')
            machine.reset()
            time.sleep(5)


main()