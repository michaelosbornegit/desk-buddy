import utime
import asyncio
import machine

from activity import Activity


# A simple activity that reboots the device
class reboot_activity(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.mount_time = utime.ticks_ms()

    async def render(self):
        self.hardware.display.clear()
        self.hardware.display.select_font(None)
        self.hardware.display.text("Rebooting to", 0, 0, 1, 0, 128, 64, 1)
        self.hardware.display.text("update...", 0, 8, 1, 0, 128, 64, 1)
        self.hardware.display.text("This is the same", 0, 24, 1, 0, 128, 64, 1)
        self.hardware.display.text("as turning your", 0, 32, 1, 0, 128, 64, 1)
        self.hardware.display.text("buddy off and on", 0, 40, 1, 0, 128, 64, 1)
        self.hardware.display.show()
        await asyncio.sleep(5)
        machine.reset()
        pass

    async def button_click(self):
        pass

    async def button_long_click(self):
        pass

    async def on_mount(self):
        self.mount_time = utime.ticks_ms()
        pass

    async def on_unmount(self):
        pass
