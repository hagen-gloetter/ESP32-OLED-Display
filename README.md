# ESP32-OLED-Display

Drive a 0.96-inch SSD1306 OLED display (128 × 64 px, I2C) with an ESP32 and MicroPython.

---

## Project Purpose

This project provides ready-to-use MicroPython modules to:

- Initialise an SSD1306 OLED display via I2C (SoftI2C).
- Display arbitrary text and graphics using the built-in `framebuf` API.
- Connect to a known WiFi network from a local credentials file.

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Microcontroller | ESP32 (tested) or ESP8266 (pin mapping differs) |
| Display | 0.96" SSD1306 OLED, 128 × 64 px, I2C interface |

### Default ESP32 Pin Wiring (I2C)

| Display Pin | ESP32 Pin |
|-------------|-----------|
| SCL         | GPIO 22   |
| SDA         | GPIO 21   |
| VCC         | 3.3 V     |
| GND         | GND       |

### ESP8266 Pin Wiring (I2C)

| Display Pin | ESP8266 Pin |
|-------------|-------------|
| SCL         | GPIO 5      |
| SDA         | GPIO 4      |
| VCC         | 3.3 V       |
| GND         | GND         |

> When using an ESP8266, uncomment the two `Pin(5)` / `Pin(4)` lines in
> `code/main.py` and `code/oled_display.py` and comment out the ESP32 lines above them.

---

## Setup & Installation

### 1. Flash MicroPython

**ESP32:**

Download the latest firmware from <https://micropython.org/download/esp32/> and flash it:

```bash
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 --baud 460800 write_flash -z 0x1000 esp32-*.bin
```

**ESP8266:**

Download the latest firmware from <https://micropython.org/download/esp8266/> and flash it:

```bash
esptool.py --chip esp8266 erase_flash
esptool.py --chip esp8266 --baud 460800 write_flash --flash_size=detect 0x0 esp8266-*.bin
```

### 2. Install a file-transfer tool

```bash
pip install mpremote
# or
pip install adafruit-ampy
```

### 3. Configure WiFi credentials

Copy the example file and fill in your network credentials:

```bash
cp secrets_wifi.json.example secrets_wifi.json
```

Edit `secrets_wifi.json`:

```json
{
  "YourSSID": "YourPassword",
  "FallbackSSID": "FallbackPassword"
}
```

> **Security note:** `secrets_wifi.json` is listed in `.gitignore` and must
> **never** be committed to version control.

### 4. Configure WebREPL password

Copy the example and set your password (8–9 characters):

```bash
cp webrepl_cfg.py.example webrepl_cfg.py
```

Edit `webrepl_cfg.py`:

```python
PASS = 'mypassword'
```

> **Security note:** `webrepl_cfg.py` is listed in `.gitignore` and must
> **never** be committed to version control.

### 5. Upload files to the ESP32

```bash
mpremote connect /dev/tty.usbserial-* cp code/ssd1306.py :
mpremote connect /dev/tty.usbserial-* cp code/oled_display.py :
mpremote connect /dev/tty.usbserial-* cp code/get_wifi_connection.py :
mpremote connect /dev/tty.usbserial-* cp secrets_wifi.json :
mpremote connect /dev/tty.usbserial-* cp webrepl_cfg.py :
mpremote connect /dev/tty.usbserial-* cp code/main.py :
```

Replace `/dev/tty.usbserial-*` with your actual serial port
(e.g. `COM3` on Windows, `/dev/ttyUSB0` on Linux).

---

## Usage

After uploading, the ESP32 boots `main.py` automatically on power-on.

```
main.py
  └─ oled_display.init_display(scl, sda)  →  returns oled object
       └─ ssd1306.SSD1306_I2C             →  low-level I2C driver
```

**Show custom text:**

```python
from machine import Pin
import oled_display

oled = oled_display.init_display(Pin(22), Pin(21))
oled.fill(0)
oled.text("Hello World", 0, 0)
oled.show()
```

**Connect to WiFi (with auto-reconnect):**

```python
import get_wifi_connection

# Initial connect
get_wifi_connection.connect_wifi()

# In your main loop – reconnects automatically if connection was lost
get_wifi_connection.ensure_wifi()

# Read current IP
ip = get_wifi_connection.get_ip()  # returns str or None

# Disconnect cleanly
get_wifi_connection.disconnect_wifi()
```

**Access WebREPL:**

After boot, WebREPL is reachable in the browser at:
```
ws://<ESP-IP>:8266
```
Use the [MicroPython WebREPL client](http://micropython.org/webrepl/) or Thonny
(*Tools → Options → Interpreter → MicroPython (ESP32/ESP8266) → WebREPL*).

## Boot Sequence

1. Display initialised
2. "Connecting WiFi" shown on OLED
3. Connect to first known network (timeout 15 s per network)
4. NTP time sync (UTC)
5. IP address shown on OLED for **5 seconds** (or "WiFi failed!" + error on failure)
6. WebREPL started
7. Main loop starts – every 10 seconds:
   - Connection checked via `get_ip()`
   - If lost: **"WiFi lost!" + CET/CEST time + error** shown on OLED → auto-reconnect
   - After reconnect: IP shown for 5 seconds, then normal display resumes

---

## Module Overview

| File | Description |
|------|-------------|
| `code/main.py` | Entry point – initialises display on boot |
| `code/oled_display.py` | `init_display()` helper + standalone demo loop |
| `code/get_wifi_connection.py` | WiFi connect / auto-reconnect / disconnect |
| `code/ssd1306.py` | SSD1306 driver (I2C & SPI) for MicroPython |
| `secrets_wifi.json.example` | Template for WiFi credentials |
| `webrepl_cfg.py.example` | Template for WebREPL password |

---

## Development Workflow

1. Edit source files locally.
2. Upload changed files with `mpremote cp` (see above).
3. Open a REPL for interactive testing:
   ```bash
   mpremote connect /dev/tty.usbserial-*
   ```
4. Soft-reset the board with `Ctrl+D` to run `main.py` again.

---

## Known Caveats

- **Hardware I2C (ESP32 only):** The ESP32 uses the hardware I2C peripheral
  (`I2C(0, freq=400_000)`) for lower CPU overhead and better timing stability.
  The ESP8266 has no hardware I2C silicon; it falls back to `SoftI2C` – see
  the commented lines in `code/oled_display.py`.
- **WiFi connect order:** Networks are tried in the order they appear in
  `secrets_wifi.json`. Put the most preferred network first.
- **Connection timeout:** 15 seconds per network attempt. Configurable via
  `_CONNECT_TIMEOUT_MS` in `get_wifi_connection.py`.
- **Time before NTP sync:** Until `ntptime.settime()` succeeds, `time.localtime()`
  returns **2000-01-01 00:00:00**. The clock on the OLED will show
  `00:00:xx CET` until the first successful WiFi connect.
- **ESP8266 RAM:** The ESP8266 has only ~35–45 KB free heap. The current
  code fits comfortably, but keep this in mind when adding features.

---

## References

- [MicroPython SSD1306 documentation](https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html)
- [Random Nerd Tutorials – ESP32 OLED](https://randomnerdtutorials.com/micropython-oled-display-esp32-esp8266/)
