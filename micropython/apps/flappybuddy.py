import random
import utime
import asyncio
import requests
import copy

from activity import Activity


class flappybuddy(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.refresh_rate = 1000 / 60  # 60fps
        self.last_render = utime.ticks_ms()
        self.user_y = 50
        self.user_y_speed = 0
        self.pipes = []
        self.last_pipe_spawn = utime.ticks_ms()
        self.pipe_spawn_rate = 2000
        self.pipe_gap = 20

    async def render(self):
        if utime.ticks_diff(utime.ticks_ms(), self.last_render) < self.refresh_rate:
            return

        display = self.hardware.display

        if (
            utime.ticks_diff(utime.ticks_ms(), self.last_pipe_spawn)
            > self.pipe_spawn_rate
        ):
            self.last_pipe_spawn = utime.ticks_ms()
            self.pipes.append({"x": 128, "y": random.randint(10, 44)})

        # Game loop
        if self.user_y < 62:
            self.user_y_speed += 0.2
            self.user_y += self.user_y_speed
        else:
            # top of screen
            self.user_y_speed = 0
            self.user_y = 62

        display.fill(0)

        for pipe in self.pipes:
            display.rect(pipe["x"], 0, 2, pipe["y"], 1)
            display.rect(pipe["x"], pipe["y"] + self.pipe_gap, 2, 64, 1)
            pipe["x"] -= 1
            if pipe["x"] < -2:
                self.pipes.remove(pipe)

        display.rect(31, round(self.user_y), 2, 2, 1)
        self.last_render = utime.ticks_ms()

    async def button_click(self):
        self.user_y_speed = -2
        # went off the screen
        if self.user_y < 0:
            self.user_y = 0
        elif self.user_y == 62:
            # unstick from bottom
            self.user_y = 61
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
