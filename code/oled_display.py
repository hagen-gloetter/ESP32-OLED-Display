from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import sys
import time


def init_display(scl, sda):
    # ESP32 Pin assignment
    #i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
    i2c = SoftI2C(scl, sda)
    # ESP8266 Pin assignment
    #i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    oled.text('init_display', 0, 0)
    oled.show()
    return oled


def main():
    display_scl = Pin(22)
    display_sda = Pin(21)
    oled = init_display(display_scl, display_sda)
    oled.text('Display on', 0, 10)
    oled.show()
    i = 0
    while True:
        oled.fill(0)
        oled.text("Temperature:", 0, 0, 1)
        oled.text("Humidity:", 0, 10, 1)
        oled.text(str(i), 110, 0, 1)
        oled.text(str(i), 110, 10, 1)
        oled.show()
#        oled.scroll(0,-11)
#        oled.text(str(i), 0, 49)
#        oled.show()
        time.sleep(1)
        i = i+1


if __name__ == '__main__':
    sys.exit(main())
