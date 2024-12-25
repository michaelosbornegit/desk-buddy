import utime
import time
import asyncio
import requests
import copy

from activity import Activity


class Dashboard(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.current_task = None
        self.last_fetch_time = utime.ticks_ms()
        self.last_render_time = utime.ticks_ms()
        self.current_dashboard_data = None

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

        # Check if it's time to fetch the dashboard
        if (
            utime.ticks_diff(curr_time, self.last_fetch_time)
            > self.functions.get_current_device_config()["dashboard"][
                "dashboardFetchInterval"
            ]
        ):
            self.last_fetch_time = curr_time
            # await fetch_dashboard()
            self.current_task = asyncio.create_task(self.fetch_dashboard())

        # Render every 0.1 seconds
        if utime.ticks_diff(curr_time, self.last_render_time) > 100:
            if self.current_dashboard_data:
                filled_in_dashbaord = copy.deepcopy(self.current_dashboard_data)
                # Replace content with what device can provide
                current_time = time.localtime()
                for row in filled_in_dashbaord:
                    for widget in row["children"]:
                        if "__CURRENT_DEVICE_TIME__" in widget["content"]:
                            widget["content"] = widget["content"].replace(
                                "__CURRENT_DEVICE_TIME__",
                                "{:02d}:{:02d}:{:02d}".format(
                                    current_time[3], current_time[4], current_time[5]
                                ),
                            )
                self.functions.set_current_raw_display(filled_in_dashbaord)
                self.last_render_time = utime.ticks_ms()

    async def button_click(self):
        pass

    async def button_long_click(self):
        await self.current_task
        await self.functions.switch_activity("MENU")

    async def on_mount(self):
        self.hardware.display.clear()
        if self.current_task:
            await self.current_task
            self.current_task.cancel()
            self.current_task = None
        self.last_fetch_time = utime.ticks_ms()
        self.current_task = asyncio.create_task(self.fetch_dashboard())

    async def on_unmount(self):
        if self.current_task:
            await self.current_task
            self.current_task.cancel()
            self.current_task = None
