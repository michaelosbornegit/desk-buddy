import math
import random
import utime

from activity import Activity

SCREEN_W = 128
SCREEN_H = 64
HUD_H = 10  # score and lives sit above this line

BRICK_COLS = 6
BRICK_ROWS = 2
BRICK_W = 19
BRICK_H = 5
BRICK_GAP = 2
BRICK_TOP = 14

PADDLE_W = 22
PADDLE_H = 2
# Kept off the bottom two rows, the executor clears them every cycle
PADDLE_Y = 58
PADDLE_SPEED = 90  # px/s while the button is held
NUDGE_PX = 8  # a quick tap still moves the paddle this far

BALL_SIZE = 2
BALL_SPEED = 40  # px/s
BALL_SPEED_STEP = 3  # px/s faster for every brick broken
SERVE_DELAY_MS = 800

DOUBLE_PRESS_MS = 300
LIVES = 3


class breakout(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.state = "title"
        self.last_tick = utime.ticks_ms()
        self.end_time = 0
        self.holding_enabled = True
        self.bricks = []
        self.lives = LIVES
        self.score = 0
        self.paddle_x = (SCREEN_W - PADDLE_W) / 2
        self.direction = -1
        self.nudge_left = 0
        self.was_pressed = False
        self.last_press = None
        self.last_was_flip = False
        self.serving = True
        self.serve_time = 0
        self.ball_x = 0
        self.ball_y = 0
        self.vx = 0
        self.vy = 0

    def start_game(self):
        self.bricks = []
        left = (SCREEN_W - (BRICK_COLS * BRICK_W + (BRICK_COLS - 1) * BRICK_GAP)) // 2
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                self.bricks.append(
                    (
                        left + col * (BRICK_W + BRICK_GAP),
                        BRICK_TOP + row * (BRICK_H + BRICK_GAP),
                    )
                )
        self.lives = LIVES
        self.score = 0
        self.paddle_x = (SCREEN_W - PADDLE_W) / 2
        self.direction = -1
        self.nudge_left = 0
        self.was_pressed = self.hardware.button.value() == 0
        self.last_press = None
        self.last_was_flip = False
        self.serve(utime.ticks_ms())
        self.state = "playing"
        # holding the button moves the paddle, so it can't mean exit while playing
        self.functions.disable_button_holding(True)
        self.holding_enabled = False

    def end_game(self, state, now):
        self.state = state
        self.end_time = now

    def ball_speed(self):
        return BALL_SPEED + BALL_SPEED_STEP * self.score

    def serve(self, now):
        self.serving = True
        self.serve_time = now

    def read_button(self, now):
        # Polled rather than using clicks so a double press is timed reliably
        pressed = self.hardware.button.value() == 0
        if pressed and not self.was_pressed:
            if (
                self.last_press is not None
                and not self.last_was_flip
                and utime.ticks_diff(now, self.last_press) < DOUBLE_PRESS_MS
            ):
                self.direction = -self.direction
                self.last_was_flip = True
            else:
                self.last_was_flip = False
            self.last_press = now
            self.nudge_left = NUDGE_PX
        self.was_pressed = pressed
        return pressed

    def move_paddle(self, pressed, dt):
        if not pressed and self.nudge_left <= 0:
            return
        step = PADDLE_SPEED * dt
        if not pressed:
            step = min(step, self.nudge_left)
        self.nudge_left = max(0, self.nudge_left - step)
        self.paddle_x = min(
            max(self.paddle_x + self.direction * step, 0), SCREEN_W - PADDLE_W
        )

    def set_speed(self, speed):
        current = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if current:
            self.vx = self.vx * speed / current
            self.vy = self.vy * speed / current

    def hit_bricks(self):
        for brick in self.bricks:
            bx, by = brick
            if (
                self.ball_x + BALL_SIZE > bx
                and self.ball_x < bx + BRICK_W
                and self.ball_y + BALL_SIZE > by
                and self.ball_y < by + BRICK_H
            ):
                # bounce off whichever side the ball is least buried in
                overlap_x = min(self.ball_x + BALL_SIZE - bx, bx + BRICK_W - self.ball_x)
                overlap_y = min(self.ball_y + BALL_SIZE - by, by + BRICK_H - self.ball_y)
                if overlap_x < overlap_y:
                    going_left = self.ball_x + BALL_SIZE / 2 < bx + BRICK_W / 2
                    self.vx = -abs(self.vx) if going_left else abs(self.vx)
                else:
                    going_up = self.ball_y + BALL_SIZE / 2 < by + BRICK_H / 2
                    self.vy = -abs(self.vy) if going_up else abs(self.vy)
                self.bricks.remove(brick)
                self.score += 1
                self.set_speed(self.ball_speed())
                return

    def move_ball(self, now, dt):
        if self.serving:
            # ride on the paddle until it launches
            self.ball_x = self.paddle_x + (PADDLE_W - BALL_SIZE) / 2
            self.ball_y = PADDLE_Y - BALL_SIZE
            if utime.ticks_diff(now, self.serve_time) > SERVE_DELAY_MS:
                self.serving = False
                speed = self.ball_speed()
                self.vx = speed * random.uniform(0.3, 0.6) * random.choice((-1, 1))
                self.vy = -math.sqrt(speed * speed - self.vx * self.vx)
            return

        # small steps so the ball can't skip through a brick or the paddle
        steps = int(max(abs(self.vx), abs(self.vy)) * dt / 1.5) + 1
        step_dt = dt / steps
        for _ in range(steps):
            self.ball_x += self.vx * step_dt
            self.ball_y += self.vy * step_dt

            if self.ball_x <= 0:
                self.ball_x = 0
                self.vx = abs(self.vx)
            elif self.ball_x >= SCREEN_W - BALL_SIZE:
                self.ball_x = SCREEN_W - BALL_SIZE
                self.vx = -abs(self.vx)
            if self.ball_y <= HUD_H:
                self.ball_y = HUD_H
                self.vy = abs(self.vy)

            if (
                self.vy > 0
                and PADDLE_Y - BALL_SIZE <= self.ball_y <= PADDLE_Y
                and self.paddle_x - BALL_SIZE < self.ball_x < self.paddle_x + PADDLE_W
            ):
                # where it lands on the paddle steers it, edges send it out wide
                offset = (self.ball_x + BALL_SIZE / 2 - self.paddle_x - PADDLE_W / 2) / (
                    PADDLE_W / 2
                )
                offset = min(max(offset, -1), 1)
                speed = self.ball_speed()
                self.vx = speed * 0.75 * offset
                self.vy = -math.sqrt(speed * speed - self.vx * self.vx)
                self.ball_y = PADDLE_Y - BALL_SIZE

            self.hit_bricks()
            if not self.bricks:
                self.end_game("won", now)
                return

            if self.ball_y > SCREEN_H:
                self.lives -= 1
                if self.lives == 0:
                    self.end_game("lost", now)
                else:
                    self.serve(now)
                return

    def draw_game(self):
        display = self.hardware.display
        display.select_font(None)
        for i in range(self.lives):
            display.fill_rect(i * 5, 2, 3, 3, 1)
        display.text(f"{self.score}/{BRICK_ROWS * BRICK_COLS}", 0, 0, 2, 0, 128, 8, 1)
        display.hline(0, HUD_H - 1, SCREEN_W, 1)

        for bx, by in self.bricks:
            display.fill_rect(bx, by, BRICK_W, BRICK_H, 1)

        paddle_x = round(self.paddle_x)
        display.fill_rect(paddle_x, PADDLE_Y, PADDLE_W, PADDLE_H, 1)
        # a notch on the leading end shows which way a press will move
        notch_x = paddle_x if self.direction < 0 else paddle_x + PADDLE_W - 4
        display.fill_rect(notch_x, PADDLE_Y - 1, 4, 1, 1)

        display.fill_rect(round(self.ball_x), round(self.ball_y), BALL_SIZE, BALL_SIZE, 1)

    def draw_message(self, title, lines):
        display = self.hardware.display
        display.select_font("text-16")
        display.text(title, 0, 0, 1, 0, 128, 64, 1)
        display.select_font(None)
        for i, line in enumerate(lines):
            display.text(line, 0, 20 + i * 9, 1, 0, 128, 64, 1)

    async def render(self):
        now = utime.ticks_ms()
        # capped so a slow frame can't teleport the ball
        dt = min(utime.ticks_diff(now, self.last_tick), 50) / 1000
        self.last_tick = now
        self.hardware.display.fill(0)

        if self.state == "title":
            self.draw_message(
                "Breakout",
                ["Tap/hold: move", "Double tap: flip", "Press to start", "Hold to exit"],
            )
        elif self.state == "playing":
            pressed = self.read_button(now)
            self.move_paddle(pressed, dt)
            self.move_ball(now, dt)
            self.draw_game()
        else:
            # wait for the button to be let go so a held move doesn't count as exit
            if (
                not self.holding_enabled
                and self.hardware.button.value() == 1
                and utime.ticks_diff(now, self.end_time) > 500
            ):
                self.functions.disable_button_holding(False)
                self.holding_enabled = True
            self.draw_message(
                "You win!" if self.state == "won" else "Game over",
                [
                    f"Score: {self.score}/{BRICK_ROWS * BRICK_COLS}",
                    "",
                    "Press to replay",
                    "Hold to exit",
                ],
            )

    async def button_click(self):
        # while playing the button is polled in render instead
        if self.state == "title" or (
            self.state in ("won", "lost") and self.holding_enabled
        ):
            self.start_game()

    async def button_long_click(self):
        await self.functions.switch_activity("dashboard")

    async def on_mount(self):
        # disable built-in displaying, the game draws everything itself
        self.functions.set_current_raw_display(None)
        self.hardware.display.load_font("text-16")

    async def on_unmount(self):
        pass
