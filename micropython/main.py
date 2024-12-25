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

from secrets import device_secret, api_host, device_id, pairing_code
from firmware import firmware_update
from hwconfig import DISPLAY, BUTTON

def connectToNetwork(ssid, ssid_password):
    DISPLAY.clear()
    DISPLAY.text("Connecting to", 0, 0, 1, 0, 128, 64, 1)
    DISPLAY.text(f"{ssid}", 0, 16, 1, 0, 128, 64, 1)
    DISPLAY.text("((i))", 0, 40, 1, 0, 128, 64, 1)
    DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
    DISPLAY.text("[o_o]", 0, 56, 1, 0, 128, 64, 1)
    DISPLAY.show()
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f'Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, ssid_password)
        timeout = 10  # seconds
        start_time = time.time()
        while not sta_if.isconnected():
            if time.time() - start_time > timeout:
                DISPLAY.clear()
                DISPLAY.text("Failed to connect", 0, 0, 1, 0, 128, 64, 1)
                DISPLAY.text("to network", 0, 8, 1, 0, 128, 64, 1)
                DISPLAY.text("Check settings", 0, 16, 1, 0, 128, 64, 1)
                DISPLAY.text("and try again", 0, 24, 1, 0, 128, 64, 1)
                DISPLAY.show()
                print('Failed to connect to network')
                time.sleep(10)
                try:
                    os.remove('wifi_config.py')
                except OSError:
                    pass
                machine.reset()
    print('Network config:', sta_if.ipconfig('addr4'))

def register():
    response = requests.post(f'{api_host}/devices/register', headers={'Authorization': device_secret},
                             json={'deviceId': device_id})

    print('Registering...')
    if response.status_code == 200:
        print('Registered successfully')
    else:
        raise Exception(f'Error registering: {response.status_code}')

    return response.json()

def main():
    button_held_time = 0
    if not BUTTON.value():
        DISPLAY.clear()
        DISPLAY.text("Keep holding", 0, 0, 1, 0, 128, 64, 1)
        DISPLAY.text('to factory', 0, 8, 1, 0, 128, 64, 1)
        DISPLAY.text("reset me...", 0, 16, 1, 0, 128, 64, 1)
        DISPLAY.text("i", 0, 40, 1, 0, 128, 64, 1)
        DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
        DISPLAY.text("[o_o]", 0, 56, 1, 0, 128, 64, 1)
        DISPLAY.show()
    while not BUTTON.value():
        button_held_time += 1
        time.sleep(0.01)
        if button_held_time >= 500:
            DISPLAY.clear()
            DISPLAY.text("Factory reset", 0, 0, 1, 0, 128, 64, 1)
            DISPLAY.text("in progress...", 0, 16, 1, 0, 128, 64, 1)
            DISPLAY.text("i", 0, 40, 1, 0, 128, 64, 1)
            DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
            DISPLAY.text("[x_x]", 0, 56, 1, 0, 128, 64, 1)
            DISPLAY.show()
            time.sleep(2)    
            try:
                os.remove('wifi_config.py')
            except OSError:
                pass

            try:
                os.remove('versions.json')
            except OSError:
                pass

            machine.reset()
    DISPLAY.clear()
    DISPLAY.text("Desk Buddy is", 0, 0, 1, 0, 128, 64, 1)
    DISPLAY.text("Starting up...", 0, 16, 1, 0, 128, 64, 1)
    DISPLAY.text("i", 0, 40, 1, 0, 128, 64, 1)
    DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
    DISPLAY.text("[o_o]", 0, 56, 1, 0, 128, 64, 1)
    DISPLAY.show()
    time.sleep(3)
    while True:
        try:
            try:
                import wifi_config
                ssid = wifi_config.ssid
                ssid_password = wifi_config.ssid_password
                connectToNetwork(ssid, ssid_password)
            except ImportError:
                import captive_portal_setup
                captive_portal_setup.main()
                break

            # Install necessary modules
            mip.install('copy')

            device_config = {}
            while True:
                try:
                    device_config = register()
                    break
                except Exception as e:
                    DISPLAY.clear()
                    DISPLAY.text("Last step!", 0, 0, 1, 0, 128, 64, 1)
                    DISPLAY.text("Scan the QR code", 0, 8, 1, 0, 128, 64, 1)
                    DISPLAY.text("under me to create", 0, 16, 1, 0, 128, 64, 1)
                    DISPLAY.text("your account", 0, 24, 1, 0, 128, 64, 1)
                    DISPLAY.text(f"Pairing code:", 0, 32, 1, 0, 128, 64, 1)
                    DISPLAY.text(f"${pairing_code}", 0, 40, 1, 0, 128, 64, 1)
                    DISPLAY.text("[o_o]", 0, 56, 1, 0, 128, 64, 1)
                    DISPLAY.show()
                    time.sleep(5)

            # Update firmware on boot
            firmware_update(device_config)

            # Import executor safely
            import executor
            asyncio.run(executor.main())
            break
        except KeyError as e:
            print(f"KeyError: {e} - Check if 'executor.py' exists and is properly named.")
        except Exception as e:
            DISPLAY.clear()
            DISPLAY.text("Desk Buddy", 0, 0, 1, 0, 128, 64, 1)
            DISPLAY.text("encountered an", 0, 8, 1, 0, 128, 64, 1)
            DISPLAY.text("irrecoverable", 0, 16, 1, 0, 128, 64, 1)
            DISPLAY.text("error", 0, 24, 1, 0, 128, 64, 1)
            DISPLAY.text("Restarting...", 0, 32, 1, 0, 128, 64, 1)
            DISPLAY.text("!", 0, 40, 1, 0, 128, 64, 1)
            DISPLAY.text("|", 0, 48, 1, 0, 128, 64, 1)
            DISPLAY.text("[x.x]", 0, 56, 1, 0, 128, 64, 1)
            DISPLAY.show()
            sys.print_exception(e)
            print('irrecoverable error, restarting...')
            time.sleep(5)
            machine.reset()

main()