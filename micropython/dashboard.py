import utime
import asyncio
import requests

from activity import Activity

class Dashboard(Activity):
    def __init__(self, name, display, led, set_current_raw_display, switch_activity, get_current_device_config, secrets):
        super().__init__(name, display, led, set_current_raw_display, switch_activity, get_current_device_config, secrets)
        # Set up instance specific variables
        self.current_task = None
        self.last_fetch_time = utime.ticks_ms()

    async def fetch_dashboard(self):
        try:
            dashboard_response = requests.get(f'{self.secrets['api_host']}/dashboards/raw/{self.secrets['device_id']}', headers = {'Authorization': self.secrets['device_secret']})
            dashboard_data = dashboard_response.json()

            self.set_current_raw_display(dashboard_data)
        except Exception as e:
            print(f'Error fetching dashboard: {e}')
    
    async def render(self):
        curr_time = utime.ticks_ms()

        # Check if it's time to fetch the dashboard
        if utime.ticks_diff(curr_time, self.last_fetch_time) > self.get_current_device_config()['dashboard']['dashboardFetchInterval']:
                self.last_fetch_time = curr_time
                # await fetch_dashboard()
                self.current_task = asyncio.create_task(self.fetch_dashboard())
    
    async def button_click(self):
        pass

    async def button_long_click(self):
        await self.switch_activity('MENU')
        pass

    async def on_mount(self):
        self.current_task = asyncio.create_task(self.fetch_dashboard())
        pass

    async def on_unmount(self):
        # clean up
        self.set_current_raw_display([])
        pass
