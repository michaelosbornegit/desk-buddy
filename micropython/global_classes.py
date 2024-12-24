class Hardware:
    def __init__(self, display, led, button):
        self.display = display
        self.led = led
        self.button = button

class Functions:
    def __init__(self, set_current_raw_display, switch_activity, get_current_device_config, disable_button_holding):
        self.set_current_raw_display = set_current_raw_display
        self.switch_activity = switch_activity
        self.get_current_device_config = get_current_device_config
        self.disable_button_holding = disable_button_holding

class Secrets:
    def __init__(self, device_secret, api_host, device_id):
        self.device_secret = device_secret
        self.api_host = api_host
        self.device_id = device_id