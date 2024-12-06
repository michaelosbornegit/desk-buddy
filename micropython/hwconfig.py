from machine import Pin
from display.enhanced_display import Enhanced_Display

DISPLAY = Enhanced_Display(bus=0, sda=Pin(6), scl=Pin(7))

BUTTON = Pin(5, Pin.IN, Pin.PULL_UP)

LED = Pin(4, Pin.OUT)
