from machine import Pin
from display.enhanced_display import Enhanced_Display
import time
import network
from secrets import ssid, ssid_password, device_secret, api_host, device_id

DISPLAY = Enhanced_Display(bus=0, sda=Pin(6), scl=Pin(7))

def connectToNetwork():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f'Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, ssid_password)
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ipconfig('addr4'))

def main():
    while True:
        try:
            # Check if we need to update firmware
            
            import executor
            executor.main()
            break
        except Exception as e:
            DISPLAY.text("Desk Buddy", 0, 0, 1, 0, 128, 64, 0)
            DISPLAY.text("encountered an", 0, 16, 1, 0, 128, 64, 0)
            DISPLAY.text("irrecoverable error", 0, 32, 1, 0, 128, 64, 0)
            DISPLAY.text("x.x", 0, 32, 1, 0, 128, 64, 0)
            print("Restarting...")
            time.sleep(5)

main()
