from machine import Pin, I2C, SoftI2C
import ssd1306
import time


def init_display(scl, sda):
    """Initialise the SSD1306 OLED display over I2C.

    Args:
        scl: SCL Pin object (ESP32 default: Pin(22)).
        sda: SDA Pin object (ESP32 default: Pin(21)).

    Returns:
        Configured SSD1306_I2C display object.
    """
    # ESP32: hardware I2C bus 0 – uses the hardware peripheral (faster, lower CPU load)
    i2c = I2C(0, scl=scl, sda=sda, freq=400000)
    # ESP8266: no hardware I2C peripheral – please change if you want to use an ESP8266
    # i2c = SoftI2C(scl=scl, sda=sda, freq=400000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    return oled


def main():
    # ESP32 default pins – change to ESP8266 lines below if you use an ESP8266
    display_scl = Pin(22)  # ESP32
    display_sda = Pin(21)  # ESP32
    # display_scl = Pin(5)  # ESP8266 – please change if you want to use an ESP8266
    # display_sda = Pin(4)  # ESP8266 – please change if you want to use an ESP8266
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
        time.sleep(1)
        i = i+1


if __name__ == '__main__':
    main()
