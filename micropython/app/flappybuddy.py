import utime
import asyncio
import requests
import copy

from activity import Activity

class FlappyBuddy(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.refresh_rate = 1000/60 # 60fps
        self.last_render = utime.ticks_ms()
        self.user_y = 50
        self.user_y_speed = 0
    
    async def render(self):
        if utime.ticks_diff(utime.ticks_ms(), self.last_render) < self.refresh_rate:
            return
        
        display = self.hardware.display

        # Game loop
        self.user_y_speed -= 0.1
        self.user_y += self.user_y_speed

        display.fill(0)
        display.rect(128/2, self.user_y, 1, 1, 1)
        pass
    
    async def button_click(self):
        self.user_y_speed = 0
        self.user_y += 10
        pass

    async def button_long_click(self):
        pass

    async def on_mount(self):
        # disable built-in displaying
        self.functions.set_current_raw_display(None)
        pass

    async def on_unmount(self):
        pass
