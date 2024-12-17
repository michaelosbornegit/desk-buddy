import network
import requests
import utime
import asyncio
from machine import Pin

from utils import get_property_if_exists
from secrets import ssid, ssid_password, device_secret, api_host, device_id
from hwconfig import DISPLAY, BUTTON, LED
from dashboard import Dashboard
from menu import Menu
from global_classes import Hardware, Functions, Secrets

# User configurable constants
DEVICE_CYCLE_INTERVAL_MS = 10 # how often the main while loop runs, play with this to get the best performance
BUTTON_LONG_PRESS_MS = 100 # how long the button needs to be held to trigger a long press

last_press_time = {}
current_raw_display = None
last_raw_display = None
current_device_config = {}
activities = []
current_activity = None
button_long_press = False
button_click = False
in_sub_menu = None

selected_menu_item = 0

def connectToNetwork():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f'Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, ssid_password)
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ipconfig('addr4'))

def display_raw(raw_data):
    global current_raw_display, last_raw_display

    current_height_offset = 0
    for index, chunk in enumerate(raw_data):
        height = get_property_if_exists(chunk, 'height') or 0
        children = get_property_if_exists(chunk, 'children') or []
        font = get_property_if_exists(chunk, 'font') or None
        # see if we need to redraw the chunk
        if not last_raw_display or len(last_raw_display) != len(current_raw_display) or (last_raw_display and chunk != last_raw_display[index]):
            DISPLAY.fill_rect(0, current_height_offset, 128, height, 0)
            current_raw_display[index] = chunk

            for child in children:
                child_content = get_property_if_exists(child, 'content') or None
                child_font = get_property_if_exists(child, 'font') or font or None
                child_height = get_property_if_exists(child, 'height') or 64
                child_width = get_property_if_exists(child, 'width') or 128
                child_x = get_property_if_exists(child, 'x') or 0
                child_y = get_property_if_exists(child, 'y') or 0
                child_horiz_align = get_property_if_exists(child, 'horizAlign') or 0
                child_vert_align = get_property_if_exists(child, 'vertAlign') or 0
                child_color = get_property_if_exists(child, 'color') or 1
                
                if not child_content:
                    # if no content, must be rectangle
                    DISPLAY.rect(child_x, current_height_offset + child_y, child_width, child_height, child_color)
                else:
                    # if content, must be text
                    if (child_font):
                        DISPLAY.load_font(child_font)

                    DISPLAY.select_font(child_font)
                    DISPLAY.text(child_content, child_x, current_height_offset + child_y, child_horiz_align, child_vert_align, child_width, child_height, child_color)

        current_height_offset += height
    
    last_raw_display = current_raw_display

async def fetch_config():
    global current_device_config
    try:
        response = requests.get(f'{api_host}/devices/config/{device_id}', headers={'Authorization': device_secret})
        current_device_config = response.json()
    except Exception as e:
        print(f'Error fetching config: {e}')

def button_pressed(event):
    global button_click
    if event.value() == 0:
        button_click = True

def get_current_device_config():
    return current_device_config

async def switch_activity(activity_name):
    global activities, current_activity
    new_activity = None
    for activity in activities:
        if activity.name == activity_name:
            new_activity = activity
            break
    
    if new_activity:
        if current_activity:
            current_activity.on_unmount()
        new_activity.on_mount()
        current_activity = new_activity
    else:
        print(f'Activity {activity_name} not found')

def set_current_raw_display(raw_display):
    global current_raw_display
    current_raw_display = raw_display

def register():
    response = requests.post(f'{api_host}/devices/register', headers={'Authorization': device_secret},
                             json={'deviceId': device_id, 'username': 'test', 'password': 'test'})

    if response.status_code == 200:
        print('Registered successfully')
    else:
        raise Exception(f'Error registering: {response.status_code}')
        
    return response.json()

async def main():
    global activities, current_device_config, on_dashboard, current_task, button_click, button_long_press, current_activity, selected_menu_item

    current_device_config = register()

    hardware = Hardware(DISPLAY, LED, BUTTON)
    functions = Functions(set_current_raw_display, switch_activity, get_current_device_config)
    secrets = Secrets(device_secret, api_host, device_id)

    activities = [
        Dashboard('DASHBOARD', hardware, functions, secrets),
        Menu('MENU', hardware, functions, secrets)
    ]

    await switch_activity('DASHBOARD')

    button_held_time = 0
    last_fetch_time = utime.ticks_ms()
    while True:        
        # Check if button is being held, give button actions priority
        if not BUTTON.value():
            button_held_time += DEVICE_CYCLE_INTERVAL_MS
            DISPLAY.fill_rect(0, 62, round(128 * (button_held_time / BUTTON_LONG_PRESS_MS)), 2, 1)
            if button_held_time > 0:
                if button_held_time >= BUTTON_LONG_PRESS_MS:
                    button_long_press = True
        else:
            # See if we need to do anything about button presses
            if button_long_press:
                button_long_press = False
                button_click = False

                await current_activity.button_long_click()
            elif button_click:
                button_click = False

                await current_activity.button_click()

            # reset long press visualization and long press timer
            DISPLAY.fill_rect(0, 62, 128, 2, 0)
            button_held_time = 0

            # No we can do anything unrelated to buttons
            # Refresh config every fetchInterval
            if current_activity.name == 'DASHBOARD':
                if utime.ticks_diff(utime.ticks_ms(), last_fetch_time) > current_device_config['configFetchInterval']:
                    last_fetch_time = utime.ticks_ms()
                    asyncio.create_task(fetch_config())

            # Allow the current activity to do its thing
            await current_activity.render()

            # Draw raw content if an activity is using it
            if current_raw_display is not None:
                display_raw(current_raw_display)

        
        # Just show once per device cycle
        DISPLAY.show()
        await asyncio.sleep_ms(DEVICE_CYCLE_INTERVAL_MS)

BUTTON.irq(handler=button_pressed, trigger=Pin.IRQ_FALLING)

asyncio.run(main())