import utime
import asyncio
import requests

from activity import Activity

class Menu(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.selected_menu_item = 0
    
    async def render(self):
        menu_items = self.functions.get_current_device_config()['menu']
        print('Menu items:', menu_items)

        raw_menu_items = []

        # First, convert to raw menu items to display
        for index, item in enumerate(menu_items):
            if index == self.selected_menu_item:
                # put inverted box to show its selected
                raw_menu_items.append({
                    'height': 16,
                    'font': 'text-16',
                    'children': [
                        {
                            'height': 16,
                            'color': 1
                        },
                        {
                            'content': item['label'],
                            'font': 'text-16',
                            'height': 16,
                            'horizAlign': 1,
                            'color': 0
                        }
                    ]
                })
            else:
                raw_menu_items.append({
                        'height': 16,
                        'font': 'text-16',
                        'children': [
                            {
                                'content': item['label'],
                                'height': 16,
                                'horizAlign': 1,
                            }
                        ]
                    })
        
        self.functions.set_current_raw_display(raw_menu_items)
    
    async def button_click(self):
        # Cycle through menu items
        if self.selected_menu_item == len(self.functions.get_current_device_config()['menu']) - 1:
            self.selected_menu_item = 0
        else:
            self.selected_menu_item += 1
        pass

    async def button_long_click(self):
        if self.selected_menu_item == len(self.functions.get_current_device_config()['menu']) - 1:
            self.hardware.display.fill_rect(0, 0, 128, 64, 0)
            await self.functions.switch_activity('DASHBOARD')
        pass

    async def on_mount(self):
        self.hardware.display.fill_rect(0, 0, 128, 64, 0)
        pass

    async def on_unmount(self):
        self.selected_menu_item = 0
        pass
