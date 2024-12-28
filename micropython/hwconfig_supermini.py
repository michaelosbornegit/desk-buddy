from machine import Pin
from display.enh_display import Enhanced_Display

DISPLAY = Enhanced_Display(bus=0, sda=Pin(8), scl=Pin(9))

BUTTON = Pin(7, Pin.IN, Pin.PULL_UP)

LED = Pin(6, Pin.OUT)
