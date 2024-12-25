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
        self.pipe_spawn_rate = 1500
        self.pipe_gap = 10
        self.pipe_speed = 1
        self.game_over = False
        self.score = 0
        self.title = True

    async def render(self):
        if self.title:
            display = self.hardware.display
            display.fill(0)
            display.load_font('text-16')
            display.select_font('text-16')
            display.text("Flappy Buddy", 0, 0, 1, 0, 128, 64, 1)
            display.select_font(None)
            display.text("Press Button", 0, 32, 1, 0, 128, 64, 1)
            display.text("To Start", 0, 40, 1, 0, 128, 64, 1)
            display.show()
            return
        elif self.game_over:
            self.functions.disable_button_holding(False)
            display = self.hardware.display
            display.fill(0)
            display.select_font('text-16')
            display.text("Game Over", 0, 0, 1, 0, 128, 64, 1)
            display.select_font(None)
            display.text(f"Score: {self.score}", 0, 32, 1, 0, 128, 64, 1)
            display.text("Press Button", 0, 40, 1, 0, 128, 64, 1)
            display.text("To Restart", 0, 48, 1, 0, 128, 64, 1)
            display.text("Hold to exit", 0, 56, 1, 0, 128, 64, 1)
            display.show()
            return
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
            pipe["x"] -= self.pipe_speed
            if pipe["x"] < -4:
                self.pipes.remove(pipe)
                continue
            display.rect(pipe["x"], 0, 2, pipe["y"], 1)
            display.rect(pipe["x"], pipe["y"] + self.pipe_gap, 2, 64, 1)
            if pipe["x"] == 30:
                self.score += 1
            if self.score % 5 == 0:
                if self.pipe_spawn_rate > 1500:
                    self.pipe_spawn_rate -= 100
                if self.pipe_gap > 15:
                    self.pipe_gap -= 1
            # check for collision
            if (
                pipe["x"] < 32
                and pipe["x"] + 2 > 31
                and (self.user_y < pipe["y"] or self.user_y > pipe["y"] + self.pipe_gap)
            ):
                self.game_over = True
            

        display.rect(31, round(self.user_y), 2, 2, 1)
        self.last_render = utime.ticks_ms()

    async def button_click(self):
        if self.title:
            self.title = False
            return
        elif self.game_over:
            self.functions.disable_button_holding(True)
            self.game_over = False
            self.user_y = 50
            self.user_y_speed = 0
            self.pipes = []
            self.pipe_speed = 1
            self.pipe_gap = 20
            self.pipe_spawn_rate = 2000
            self.score = 0
            return
        self.user_y_speed = -2
        # went off the screen
        if self.user_y < 0:
            self.user_y = 0
        elif self.user_y == 62:
            # unstick from bottom
            self.user_y = 61
        pass

    async def button_long_click(self):
        await self.functions.switch_activity("dashboard")

    async def on_mount(self):
        # disable built-in displaying
        self.functions.set_current_raw_display(None)
        # disable button holding (it messes with gameplay)
        self.functions.disable_button_holding()
        pass

    async def on_unmount(self):
        pass
