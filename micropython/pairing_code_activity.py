from secrets import pairing_code

from activity import Activity


# A simple activity that displays the pairing code
class pairing_code_activity(Activity):
    def __init__(self, name, hardware, functions, secrets):
        super().__init__(name, hardware, functions, secrets)
        self.is_rendered = False

    async def render(self):
        # Only render once
        if self.is_rendered:
            return
        self.hardware.display.clear()
        self.hardware.display.select_font(None)
        self.hardware.display.text("Pairing code:", 0, 0, 1, 0, 128, 64, 1)
        self.hardware.display.select_font("text-16")
        self.hardware.display.text(f"{pairing_code}", 0, 16, 1, 0, 128, 64, 1)
        self.hardware.display.select_font(None)
        self.hardware.display.text("Press Button", 0, 40, 1, 0, 128, 64, 1)
        self.hardware.display.text("To exit", 0, 48, 1, 0, 128, 64, 1)
        self.hardware.display.show()
        self.is_rendered = True

    async def button_click(self):
        await self.functions.switch_activity("dashboard")

    async def button_long_click(self):
        await self.functions.switch_activity("dashboard")

    async def on_mount(self):
        pass

    async def on_unmount(self):
        pass
