from machine import Pin, reset
import time
import ntptime
import webrepl
import oled_display
import get_wifi_connection

# ESP32 default pins – change to ESP8266 lines below if you use an ESP8266
display_scl = Pin(22)  # ESP32
display_sda = Pin(21)  # ESP32
# display_scl = Pin(5)  # ESP8266 – please change if you want to use an ESP8266
# display_sda = Pin(4)  # ESP8266 – please change if you want to use an ESP8266
oled = oled_display.init_display(display_scl, display_sda)

_webrepl_started = False


def _start_webrepl():
    """Start WebREPL only once per boot (calling start() repeatedly is unsafe)."""
    global _webrepl_started
    if not _webrepl_started:
        webrepl.start()
        _webrepl_started = True
        print("WebREPL started")


def _show_ip(label="Connected!"):
    ip = get_wifi_connection.get_ip() or "unknown"
    oled.fill(0)
    oled.text(label, 0, 0)
    oled.text(ip, 0, 20)
    oled.show()
    time.sleep(5)


def _sync_ntp(retries=3):
    for attempt in range(retries):
        try:
            ntptime.settime()
            print("NTP time synchronised")
            return
        except Exception as e:
            print(f"NTP sync failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2)


def _is_dst():
    """Return True if CEST (UTC+2) is active, False for CET (UTC+1).

    Transition rules (EU):
      - CEST starts: last Sunday in March  at 02:00 UTC  (clocks → 03:00)
      - CET  starts: last Sunday in October at 01:00 UTC (clocks → 02:00)
    Uses UTC time (as provided by ntptime) for the calculation.
    """
    t = time.localtime()
    month, day, hour, weekday = t[1], t[2], t[3], t[6]
    # weekday: 0 = Monday … 6 = Sunday (MicroPython convention)
    if month < 3 or month > 10:
        return False
    if 3 < month < 10:
        return True
    # days elapsed since the most recent Sunday (0 if today is Sunday)
    days_since_sun = (weekday + 1) % 7
    last_sun = day - days_since_sun          # day-of-month of the last Sunday
    if month == 3:                           # spring forward
        return last_sun >= 25 and (day > last_sun or hour >= 2)
    # October – fall back
    return not (last_sun >= 25 and (day > last_sun or hour >= 1))


def _time_str():
    """Return local time as 'HH:MM:SS CET ' or 'HH:MM:SS CEST' string."""
    dst = _is_dst()
    offset = 7200 if dst else 3600
    t = time.localtime(time.time() + offset)
    tz = "CEST" if dst else "CET "          # same width (4 chars) to avoid display artefacts
    return "{:02d}:{:02d}:{:02d} {}".format(t[3], t[4], t[5], tz)


# --- WiFi connect --------------------------------------------------------
oled.fill(0)
oled.text("Connecting WiFi", 0, 0)
oled.show()

try:
    get_wifi_connection.connect_wifi()
    _sync_ntp()
    _show_ip("Connected!")
    _start_webrepl()
except OSError as e:
    print(f"WiFi error: {e}")
    oled.fill(0)
    oled.text("WiFi failed!", 0, 0)
    oled.text(str(e)[:16], 0, 20)
    oled.show()
    time.sleep(5)

# --- Main display loop ---------------------------------------------------
# Line 0  (y=0):  clock  HH:MM:SS CET/CEST  – updated every second
# Lines below are free for application content
_wifi_tick = 0
_ntp_tick = 0
_NTP_RESYNC_INTERVAL = 3600  # re-sync NTP every hour (in seconds)
_CONSECUTIVE_ERRORS = 0
_MAX_CONSECUTIVE_ERRORS = 30  # reset board after 30 consecutive failures

while True:
    try:
        # --- Refresh clock line (first 8 px row) ---
        oled.fill_rect(0, 0, 128, 8, 0)
        oled.text(_time_str(), 0, 0)
        oled.show()
        _CONSECUTIVE_ERRORS = 0  # display update succeeded

        # --- Check WiFi every 10 seconds ---
        _wifi_tick += 1
        if _wifi_tick >= 10:
            _wifi_tick = 0
            if get_wifi_connection.get_ip() is None:
                ts = _time_str()
                print(f"WiFi lost at {ts} – reconnecting...")
                oled.fill(0)
                oled.text("WiFi lost!", 0, 0)
                oled.text(ts, 0, 12)
                oled.text("Reconnecting...", 0, 24)
                oled.show()

                try:
                    get_wifi_connection.ensure_wifi()
                    _sync_ntp()
                    _start_webrepl()
                    _show_ip("Reconnected!")
                except OSError as e:
                    ts = _time_str()
                    print(f"Reconnect failed at {ts}: {e}")
                    oled.fill(0)
                    oled.text("WiFi lost!", 0, 0)
                    oled.text(ts, 0, 12)
                    oled.text(str(e)[:16], 0, 24)
                    oled.show()
                    time.sleep(10)  # back-off before next retry

        # --- Periodic NTP re-sync ---
        _ntp_tick += 1
        if _ntp_tick >= _NTP_RESYNC_INTERVAL:
            _ntp_tick = 0
            if get_wifi_connection.get_ip() is not None:
                _sync_ntp(retries=1)

    except Exception as e:
        # Catch transient I2C / hardware errors to prevent permanent crash
        _CONSECUTIVE_ERRORS += 1
        print(f"Main loop error ({_CONSECUTIVE_ERRORS}): {e}")
        if _CONSECUTIVE_ERRORS >= _MAX_CONSECUTIVE_ERRORS:
            print("Too many consecutive errors – resetting board")
            reset()
        time.sleep(1)
        continue

    time.sleep(1)