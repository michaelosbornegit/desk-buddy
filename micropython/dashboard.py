import utime
import asyncio
import requests

from activity import Activity

class Dashboard(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.current_task = None
        self.last_fetch_time = utime.ticks_ms()

    async def fetch_dashboard(self):
        try:
            dashboard_response = requests.get(f'{self.secrets.api_host}/dashboards/raw/{self.secrets.device_id}', headers = {'Authorization': self.secrets.device_secret})
            dashboard_data = dashboard_response.json()

            self.functions.set_current_raw_display(dashboard_data)
        except Exception as e:
            print(f'Error fetching dashboard: {e}')
    
    async def render(self):
        curr_time = utime.ticks_ms()

        # Check if it's time to fetch the dashboard
        if utime.ticks_diff(curr_time, self.last_fetch_time) > self.functions.get_current_device_config()['dashboard']['dashboardFetchInterval']:
                self.last_fetch_time = curr_time
                # await fetch_dashboard()
                self.current_task = asyncio.create_task(self.fetch_dashboard())
    
    async def button_click(self):
        pass

    async def button_long_click(self):
        await self.current_task
        await self.functions.switch_activity('MENU')

    async def on_mount(self):
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
