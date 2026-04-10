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

> For ESP8266 change the pins to SCL = GPIO 5 and SDA = GPIO 4.

---

## Setup & Installation

### 1. Flash MicroPython

Download the latest MicroPython firmware for ESP32 from
<https://micropython.org/download/esp32/> and flash it:

```bash
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 --baud 460800 write_flash -z 0x1000 esp32-*.bin
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

## Boot Sequence

1. Display initialised
2. "Connecting WiFi" shown on OLED
3. Connect to first known network (timeout 15 s per network)
4. NTP time sync (UTC)
5. IP address shown on OLED for **5 seconds** (or "WiFi failed!" + error on failure)
6. WebREPL started
7. Main loop starts – every 10 seconds:
   - Connection checked via `get_ip()`
   - If lost: **"WiFi lost!" + UTC time + error** shown on OLED → auto-reconnect
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

- `SoftI2C` is used rather than hardware I2C driver – sufficient for a 400 kHz display bus but may be slower than `I2C`.
- The WiFi module scans for all configured SSIDs and connects to the **first one found**. Adjust priority by ordering keys in `secrets_wifi.json`.
- Connection timeout is set to **15 seconds** per network (`_CONNECT_TIMEOUT_MS` in `get_wifi_connection.py`).
- Time shown on OLED is **UTC** (set via NTP after connect). No timezone conversion is applied.
- WebREPL is accessible at `ws://<IP>:8266` using the [MicroPython WebREPL client](http://micropython.org/webrepl/) or a WebREPL-compatible tool (e.g. Thonny).

---

## References

- [MicroPython SSD1306 documentation](https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html)
- [Random Nerd Tutorials – ESP32 OLED](https://randomnerdtutorials.com/micropython-oled-display-esp32-esp8266/)
