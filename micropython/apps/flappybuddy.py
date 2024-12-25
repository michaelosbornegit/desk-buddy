import utime
import asyncio
import requests
import copy

from activity import Activity


class flappybuddy(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.refresh_rate = 1000 / 120  # 120fps
        self.last_render = utime.ticks_ms()
        self.user_y = 50
        self.user_y_speed = 0

    async def render(self):
        if utime.ticks_diff(utime.ticks_ms(), self.last_render) < self.refresh_rate:
            return

        display = self.hardware.display

        # Game loop
        if self.user_y < 63:
            self.user_y_speed += 0.2
            self.user_y += self.user_y_speed
        else:
            # top of screen
            self.user_y_speed = 0
            self.user_y = 63

        display.fill(0)

        display.rect(31, round(self.user_y), 1, 1, 1)
        pass

    async def button_click(self):
        self.user_y_speed = -2
        # went off the screen
        if self.user_y < 0:
            self.user_y = 0
        elif self.user_y == 63:
            # unstick from bottom
            self.user_y = 62
        pass

    async def button_long_click(self):
        pass

    async def on_mount(self):
        # disable built-in displaying
        self.functions.set_current_raw_display(None)
        # disable button holding (it messes with gameplay)
        self.functions.disable_button_holding()
        pass

    async def on_unmount(self):
        pass
