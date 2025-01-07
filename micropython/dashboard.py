from utils import get_los_angeles_time, get_property_if_exists
import utime
import time
import asyncio
import requests
import copy
import machine

from activity import Activity
import sys
import executor

LED_BLINK_INTERVAL_MS = 5000  # how often the LED blinks
LED_BLINK_DURATION_MS = 10  # how long the LED blinks for


class dashboard(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.current_tasks = [None, None]
        self.last_dashboard_fetch_time = utime.ticks_ms()
        self.last_config_fetch_time = utime.ticks_ms()
        self.last_blink_time = utime.ticks_ms()
        self.last_render_time = utime.ticks_ms()
        self.current_dashboard_data = None

    async def fetch_config(self):
        try:
            response = requests.get(
                f"{self.secrets.api_host}/devices/config/{self.secrets.device_id}",
                headers={"Authorization": self.secrets.device_secret},
            )
            self.functions.set_current_device_config(response.json())
        except Exception as e:
            print(f"Error fetching config: {e}")

    async def fetch_dashboard(self):
        try:
            dashboard_response = requests.get(
                f"{self.secrets.api_host}/dashboards/raw/{self.secrets.device_id}",
                headers={"Authorization": self.secrets.device_secret},
            )
            self.current_dashboard_data = dashboard_response.json()

        except Exception as e:
            print(f"Error fetching dashboard: {e}")

    async def render(self):
        curr_time = utime.ticks_ms()

        # Check if it's time to refresh dashboard data
        if (
            utime.ticks_diff(curr_time, self.last_dashboard_fetch_time)
            > self.functions.get_current_device_config()["dashboard"][
                "dashboardFetchInterval"
            ]
        ):
            self.last_dashboard_fetch_time = curr_time

            # don't allow multiple fetches to happen at once
            if self.current_tasks[0] and self.current_tasks[0].done():
                self.current_tasks[0] = asyncio.create_task(self.fetch_dashboard())

        # Check if it's time to refresh device config
        if (
            utime.ticks_diff(curr_time, self.last_config_fetch_time)
            > self.functions.get_current_device_config()["configFetchInterval"]
        ):
            self.last_config_fetch_time = utime.ticks_ms()
            # don't allow multiple fetches to happen at once
            if self.current_tasks[1] and self.current_tasks[1].done():
                self.current_tasks[1] = asyncio.create_task(self.fetch_config())

        # Check if we need to blink the LED for notifications
        if (
            self.functions.get_current_device_config()
            and len(self.functions.get_current_device_config()["notifications"]) > 0
        ):
            if (
                utime.ticks_diff(utime.ticks_ms(), self.last_blink_time)
            ) > LED_BLINK_INTERVAL_MS:
                self.last_blink_time = utime.ticks_ms()
                self.hardware.led.on()
            if (self.hardware.led.value() == 1) and (
                utime.ticks_diff(utime.ticks_ms(), self.last_blink_time)
                > LED_BLINK_DURATION_MS
            ):
                self.hardware.led.off()

        # Render every 0.3 seconds
        if utime.ticks_diff(curr_time, self.last_render_time) > 300:
            if self.current_dashboard_data:
                filled_in_dashboard = copy.deepcopy(self.current_dashboard_data)
                # Replace content with what device can provide
                current_time = get_los_angeles_time()
                for row in filled_in_dashboard:
                    for widget in row["children"]:
                        if "__CURRENT_DEVICE_TIME__" in widget["content"]:
                            hour = current_time[3]
                            am_pm = "AM" if hour < 12 else "PM"
                            hour = hour % 12
                            hour = 12 if hour == 0 else hour
                            widget["content"] = widget["content"].replace(
                                "__CURRENT_DEVICE_TIME__",
                                "{:01d}:{:02d}:{:02d} {}".format(
                                    hour, current_time[4], current_time[5], am_pm
                                ),
                            )
                self.functions.set_current_raw_display(filled_in_dashboard)
                self.last_render_time = utime.ticks_ms()

    async def button_click(self):
        if get_property_if_exists(
            self.functions.get_current_device_config(), "devMode"
        ):
            print("Dev mode enabled, rebooting!")
            machine.soft_reset()

    async def button_long_click(self):
        for task in self.current_tasks:
            if task:
                task.cancel()

        await self.functions.load_new_activity("menu")
        await self.functions.switch_activity("menu")

    async def on_mount(self):
        # Ensure we render the dashboard immediately
        self.last_render_time = utime.ticks_ms() - 60000
        self.current_dashboard_data = None
        self.hardware.display.clear()
        for task in self.current_tasks:
            if task:
                task.cancel()
        self.last_dashboard_fetch_time = utime.ticks_ms()
        self.last_config_fetch_time = utime.ticks_ms()
        self.current_tasks[0] = asyncio.create_task(self.fetch_dashboard())
        self.current_tasks[1] = asyncio.create_task(self.fetch_config())

    async def on_unmount(self):
        for task in self.current_tasks:
            if task:
                task.cancel()
