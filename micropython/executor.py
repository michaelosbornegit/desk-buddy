import network
import requests
import utime
import asyncio
import gc
from machine import Pin

from utils import get_property_if_exists
from secrets import device_secret, api_host, device_id
from hwconfig import DISPLAY, BUTTON, LED
from dashboard import dashboard
from menu import menu
from notifications import notifications
from global_classes import Hardware, Functions, Secrets

# User configurable constants
DEVICE_CYCLE_INTERVAL_MS = (
    10  # how often the main while loop runs, play with this to get the best performance
)
BUTTON_LONG_PRESS_MS = (
    100  # how long the button needs to be held to trigger a long press
)

last_press_time = {}
current_raw_display = None
last_raw_display = None
current_device_config = {}
activities = []
current_activity = None
button_long_press = False
button_click = False
button_holding_disabled = False
functions = None
hardware = None
secrets = None


def display_raw(raw_data):
    global current_raw_display, last_raw_display

    current_height_offset = 0
    for index, chunk in enumerate(raw_data):
        height = get_property_if_exists(chunk, "height") or 0
        children = get_property_if_exists(chunk, "children") or []
        font = get_property_if_exists(chunk, "font") or None
        # see if we need to redraw the chunk
        if (
            not last_raw_display
            or len(last_raw_display) != len(current_raw_display)
            or (last_raw_display and chunk != last_raw_display[index])
        ):
            DISPLAY.fill_rect(0, current_height_offset, 128, height, 0)
            current_raw_display[index] = chunk

            for child in children:
                child_content = get_property_if_exists(child, "content") or None
                child_font = get_property_if_exists(child, "font") or font or None
                child_height = get_property_if_exists(child, "height") or 64
                child_width = get_property_if_exists(child, "width") or 128
                child_x = get_property_if_exists(child, "x") or 0
                child_y = get_property_if_exists(child, "y") or 0
                child_horiz_align = get_property_if_exists(child, "horizAlign") or 0
                child_vert_align = get_property_if_exists(child, "vertAlign") or 0
                child_color = get_property_if_exists(child, "color") or 1

                if not child_content:
                    # if no content, must be rectangle
                    DISPLAY.rect(
                        child_x,
                        current_height_offset + child_y,
                        child_width,
                        child_height,
                        child_color,
                    )
                else:
                    # if content, must be text
                    if child_font:
                        DISPLAY.load_font(child_font)

                    DISPLAY.select_font(child_font)
                    DISPLAY.text(
                        child_content,
                        child_x,
                        current_height_offset + child_y,
                        child_horiz_align,
                        child_vert_align,
                        child_width,
                        child_height,
                        child_color,
                    )

        current_height_offset += height

    last_raw_display = current_raw_display


def button_pressed(event):
    global button_click
    if event.value() == 0:
        button_click = True


def get_current_device_config():
    return current_device_config


def set_current_device_config(new_config):
    global current_device_config
    current_device_config = new_config


def set_current_raw_display(raw_display):
    global current_raw_display, last_raw_display
    current_raw_display = raw_display
    last_raw_display = None


def disable_button_holding(value=True):
    global button_holding_disabled
    button_holding_disabled = value


async def switch_activity(activity_name):
    global \
        activities, \
        current_activity, \
        button_holding_disabled, \
        current_raw_display, \
        last_raw_display
    new_activity = None
    for activity in activities:
        if activity.name == activity_name:
            new_activity = activity
            break

    if new_activity:
        # Reset things that should always be reset between activities
        current_raw_display = None
        last_raw_display = None
        DISPLAY.clear()
        LED.off()
        button_holding_disabled = False
        if current_activity:
            await current_activity.on_unmount()
        gc.collect()
        await new_activity.on_mount()
        current_activity = new_activity
    else:
        print(f"Activity {activity_name} not found. Is it loaded?")


async def unload_activity(path):
    global activities
    fileName = path.split("/")[-1]
    activityName = fileName.split(".")[0]
    # remove existing clones of the activity
    # to hopefully get garbage collected
    for index, existing_activity in enumerate(activities):
        if existing_activity.name == activityName:
            activities.pop(index)


async def load_new_activity(path):
    global activities, functions, hardware, secrets
    await unload_activity(path)
    fileName = path.split("/")[-1]
    activityName = fileName.split(".")[0]

    module = __import__(path.split(".")[0])
    activity = getattr(module, activityName)
    activities.append(activity(activityName, hardware, functions, secrets))


def register():
    response = requests.post(
        f"{api_host}/devices/register",
        headers={"Authorization": device_secret},
        json={"deviceId": device_id},
    )

    if response.status_code == 200:
        print("Registered successfully")
    else:
        raise Exception(f"Error registering: {response.status_code}")

    return response.json()


async def main():
    global \
        activities, \
        current_activity, \
        current_device_config, \
        on_dashboard, \
        current_task, \
        button_click, \
        button_long_press, \
        hardware, \
        functions, \
        secrets

    current_device_config = register()

    hardware = Hardware(DISPLAY, LED, BUTTON)
    functions = Functions(
        set_current_raw_display,
        switch_activity,
        get_current_device_config,
        set_current_device_config,
        disable_button_holding,
        load_new_activity,
        unload_activity,
    )
    secrets = Secrets(device_secret, api_host, device_id)

    activities = []

    await load_new_activity("dashboard.py")
    await switch_activity("dashboard")

    # prerender dashboard
    await current_activity.render()

    button_held_time = 0
    while True:
        # Check if button is being held, give button actions priority
        if not BUTTON.value() and not button_holding_disabled:
            button_held_time += DEVICE_CYCLE_INTERVAL_MS
            DISPLAY.fill_rect(
                0, 62, round(128 * (button_held_time / BUTTON_LONG_PRESS_MS)), 2, 1
            )
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

            # Now we can do anything unrelated to buttons

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
