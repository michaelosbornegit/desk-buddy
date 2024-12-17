from machine import Pin
from display.enhanced_display import Enhanced_Display
import time
import network
import requests
import esp32
from secrets import ssid, ssid_password, device_secret, api_host, device_id

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
            # TODO Do the whole captive portal wifi thing
            connectToNetwork()
            device_config = register()

            nvs_modified = False
            # Check if we need to update firmware
            for firmware in device_config['firmware']:
                try:
                    nvs.get_i32(firmware['relative_path'])
                except OSError: # key doesn't exist
                    # download and save file contents
                    firmware_response = requests.get(f'{api_host}/firmware/{firmware["relative_path"]}', headers={'Authorization': device_secret})
                    
                    with open(firmware['relative_path'], 'wb') as f:
                        print(f'Writing firmware to {firmware["relative_path"]}')
                        f.write(firmware_response.content)
                    nvs.set_i32(firmware['relative_path'], firmware['version'])
                    nvs_modified = True
            
            if nvs_modified:
                nvs.commit()
                
            import executor
            executor.main()
            break
        except Exception as e:
            DISPLAY.text("Desk Buddy", 0, 0, 1, 0, 128, 64, 0)
            DISPLAY.text("encountered an", 0, 16, 1, 0, 128, 64, 0)
            DISPLAY.text("irrecoverable error", 0, 32, 1, 0, 128, 64, 0)
            DISPLAY.text("x.x", 0, 32, 1, 0, 128, 64, 0)
            DISPLAY.text("Restarting in 5s...", 0, 48, 1, 0, 128, 64, 0)
            DISPLAY.show()
            time.sleep(5)

main()
