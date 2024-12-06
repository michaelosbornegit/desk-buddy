class Activity:
    
    def __init__(self, name, display, led, set_current_raw_display, switch_activity, get_current_device_config, secrets):
        self.name = name
        self.display = display
        self.led = led
        self.set_current_raw_display = set_current_raw_display
        self.switch_activity = switch_activity
        self.get_current_device_config = get_current_device_config
        self.secrets = secrets

    async def render(self):
        raise NotImplementedError("Subclasses must implement 'render' method.")
    
    async def button_click(self):
        raise NotImplementedError("Subclasses must implement 'button_click' method.")
    
    async def button_long_click(self):
        raise NotImplementedError("Subclasses must implement 'button_long_click' method.")
    
    async def on_mount(self):
        raise NotImplementedError("Subclasses must implement 'on_mount' method.")

    async def on_unmount(self):
        raise NotImplementedError("Subclasses must implement 'on_unmount' method.")