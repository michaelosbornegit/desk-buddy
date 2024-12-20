import utime
import asyncio
import requests
import copy

from activity import Activity

class Menu(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        # Set up instance specific variables
        self.selected_menu_item = 0
        self.current_sub_menu = None
    
    async def render(self):
        menu_items = self.functions.get_current_device_config()['menu']

        # Deep clone menu_items
        menu_items = copy.deepcopy(menu_items)

        menu_items.append({
            'label': 'Back'
        })

        # First, convert to raw menu items to display
        for index, item in enumerate(list(reversed(menu_items))):
            if index == self.selected_menu_item:
                # put inverted box to show its selected
                self.current_raw_menu.append({
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
                self.current_raw_menu.append({
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

        self.current_raw_menu = list(reversed(self.current_raw_menu))
        self.functions.set_current_raw_display(self.current_raw_menu)
    
    async def button_click(self):
        # Cycle through menu items
        if self.selected_menu_item == len(self.current_raw_menu) - 1:
            self.selected_menu_item = 0
        else:
            self.selected_menu_item += 1

    async def button_long_click(self):
        if self.selected_menu_item == len(self.current_raw_menu) - 1:
            self.hardware.display.clear()
            await self.functions.switch_activity('DASHBOARD')

    async def on_mount(self):
        self.hardware.display.clear()

    async def on_unmount(self):
        self.selected_menu_item = 0
