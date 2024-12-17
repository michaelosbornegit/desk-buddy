from global_classes import Hardware, Functions, Secrets

class Activity:
    def __init__(self, name, hardware, functions, secrets):
        self.name = name
        self.hardware: Hardware = hardware
        self.functions: Functions = functions
        self.secrets: Secrets = secrets

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