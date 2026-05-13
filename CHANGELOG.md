# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

#### `ssd1306.py`
- **Vollständige FrameBuffer-Delegation:** `rect()`, `hline()`, `vline()`,
  `line()` und `blit()` an die `SSD1306`-Basisklasse delegiert – alle
  FrameBuffer-Zeichenoperationen sind nun direkt am Display-Objekt verfügbar.

#### `main.py`
- **Periodischer NTP-Re-Sync:** Die Uhrzeit wird jetzt stündlich erneut per
  NTP synchronisiert (konfigurierbar über `_NTP_RESYNC_INTERVAL`).
- **NTP-Retry:** `_sync_ntp()` versucht bis zu 3× mit 2 s Pause (statt
  single-shot), um kurzfristige DNS-/Netzwerk-Ausfälle abzufangen.
- **Hardware-Watchdog:** Bei ≥ 30 aufeinanderfolgenden Fehlern im Main-Loop
  wird `machine.reset()` ausgelöst, um das Board aus einem dauerhaften
  Fehlerzustand zu befreien.
- **Exception-Handler im Main-Loop:** Transiente I2C-/Hardware-Fehler
  crashen nicht mehr dauerhaft – nach einem kurzen Back-off läuft der Loop
  weiter.

### Fixed

#### `ssd1306.py`
- **Bug fix (missing `fill_rect` delegation):** Added `fill_rect()` method to
  the `SSD1306` base class. The method was missing from the framebuffer
  delegation layer, causing `AttributeError` at runtime when `main.py` called
  `oled.fill_rect()` to clear the clock line.

#### `main.py`
- **WebREPL-Doppelstart vermieden:** `webrepl.start()` wird jetzt nur einmal
  pro Boot aufgerufen (via `_start_webrepl()`). Wiederholte Aufrufe nach
  Reconnect konnten zu internen Fehlern führen.

### Changed

#### `ssd1306.py`
- **Deprecated API replaced:** Replaced `framebuf.FrameBuffer1` with
  `framebuf.FrameBuffer(..., framebuf.MONO_VLSB)` in both `SSD1306_I2C` and
  `SSD1306_SPI`. `FrameBuffer1` is deprecated in current MicroPython and may
  be removed in a future release.

#### `get_wifi_connection.py`
- **CPU-Last reduziert:** `machine.idle()` im Connect-Busy-Wait durch
  `time.sleep_ms(100)` ersetzt – definiert 100 ms Pause pro Iteration statt
  undefiniertem Idle-Verhalten. `machine`-Import entfernt.
- **Sauberes Disconnect:** `disconnect_wifi()` deaktiviert jetzt auch das
  WLAN-Interface (`active(False)`), um Strom zu sparen.

#### `oled_display.py`
- Ungenutzten `SoftI2C`-Import aus der aktiven Import-Zeile entfernt (bleibt
  als Kommentar für ESP8266-Nutzer erhalten).

---

## [0.1.0] – 2026-04-10

### Added
- **Hardware I2C auf ESP32** (`oled_display.py`): Wechsel von `SoftI2C` auf
  `machine.I2C(0, freq=400_000)` – nutzt den Hardware-I2C-Peripheral des ESP32
  für geringere CPU-Last und stabileres Timing. Der ESP8266 hat keine Hardware-I2C-
  Einheit; die kommentierte `SoftI2C`-Alternative bleibt erhalten.
- **Mehrere WLANs in `secrets_wifi.json.example`**: Drei Beispieleinträge
  (Home, Office, Hotspot) machen die JSON-Syntax für mehrere Netzwerke sofort
  erkennbar.
- **README Known Caveats überarbeitet**: CET/CEST und WebREPL (beides Features,
  keine Einschränkungen) aus den Caveats entfernt. Neu dokumentiert: Hardware I2C
  vs. SoftI2C (ESP8266), Zeitanzeige vor dem ersten NTP-Sync (2000-01-01),
  ESP8266-RAM-Einschränkung. WebREPL-Zugangsdoku in den Usage-Abschnitt verschoben.
- **Echtzeit-Uhr auf dem Display** (`main.py`): Die erste Zeile des OLED-Displays
  zeigt permanent die aktuelle Lokalzeit (`HH:MM:SS CET ` bzw. `HH:MM:SS CEST`) und
  wird jede Sekunde aktualisiert. Sommer-/Winterzeit (EU-Regel: letzter Sonntag im
  März 02:00 UTC / letzter Sonntag im Oktober 01:00 UTC) wird automatisch
  berücksichtigt. Nur die oberste Zeile wird neu gezeichnet (`fill_rect`), um
  Bildschirmflackern zu minimieren. Der WiFi-Check läuft weiterhin alle 10 Sekunden.
- **OLED WiFi-lost Anzeige** (`main.py`): Bei verlorener WLAN-Verbindung zeigt
  das Display sofort "WiFi lost!", die aktuelle UTC-Uhrzeit und den
  Fehlertext an. Nach erfolgreichem Reconnect erscheint erneut die IP-Adresse
  für 5 Sekunden.
- **NTP-Zeitsynchronisation** (`main.py`): Nach jedem (Re-)Connect wird
  `ntptime.settime()` aufgerufen, sodass `time.localtime()` die echte
  UTC-Zeit liefert.
- **WebREPL** (`main.py`): `webrepl.start()` wird nach erfolgreichem
  WiFi-Connect gestartet (und nach jedem Reconnect neu initialisiert).
  Das Passwort wird aus `webrepl_cfg.py` gelesen.
- `webrepl_cfg.py.example` – Template für das WebREPL-Passwort.
- `webrepl_cfg.py` in `.gitignore` eingetragen (enthält Passwort).
- **Auto-WiFi-Reconnect** (`get_wifi_connection.ensure_wifi()`): Erkennt eine
  verlorene Verbindung und baut sie automatisch neu auf. Wird alle 10 Sekunden
  aus dem Main-Loop heraus aufgerufen.
- **IP-Anzeige beim Boot** (`main.py`): Nach erfolgreichem Verbindungsaufbau
  wird die IP-Adresse des ESP32 für 5 Sekunden auf dem OLED-Display angezeigt.
  Bei einem Verbindungsfehler erscheint stattdessen "WiFi failed!" + Fehlertext.
- `get_ip()` in `get_wifi_connection.py`: Gibt die aktuelle IP-Adresse zurück
  oder `None` wenn nicht verbunden.
- `secrets_wifi.json.example` – Template für WiFi-Credentials.
- `.gitignore` Einträge für `secrets_wifi.json`, `*.mpy`, `.DS_Store` und
  `webrepl_cfg.py`.
- Umfangreiches `README.md` mit Hardware-Verdrahtung, Installationsanleitung,
  Verwendungsbeispielen, Modulübersicht und Hinweisen.
- `CHANGELOG.md` (diese Datei).
- Docstrings für `oled_display.init_display()` und alle Funktionen in
  `get_wifi_connection.py`.

### Changed

#### `get_wifi_connection.py`
- **Bug fix (SSID matching):** Replaced `if ssid in str(nets)` with a proper
  comparison against decoded SSID strings extracted from scan-result tuples.
  The old approach converted the entire scan-result list to a raw string,
  which could produce false-positive matches (e.g. SSID `"AB"` matching a
  network named `"ABCD"`).
- **Bug fix (infinite loop):** Added a 15-second connection timeout
  (`_CONNECT_TIMEOUT_MS = 15000`) using `time.ticks_ms()` /
  `time.ticks_diff()`. The previous code could hang indefinitely if a network
  was reachable but the password was wrong or the AP was unresponsive.
- **Bug fix (NameError on disconnect):** `_wifi` is now initialised to `None`
  at module level. Calling `disconnect_wifi()` before `connect_wifi()` no
  longer raises `NameError`.
- **Bug fix (resource leak):** `open("secrets_wifi.json")` is now wrapped in
  a `with` statement so the file handle is always closed.
- **Bug fix (misleading error message):** The per-network error message no
  longer incorrectly states "Failed to connect to any known network". A
  per-network message and a final `OSError` are now raised instead.
- Moved all imports to module level (previously inside the function body).
- Removed extensive commented-out debug `print` statements.
- Renamed module-global `wifi` → `_wifi` to signal it is private.

#### `oled_display.py`
- **Bug fix (debug artefact):** Removed `oled.text('init_display', 0, 0)` and
  `oled.show()` from `init_display()`. These lines wrote a hardcoded debug
  string to the display on every initialisation, which would overwrite the
  caller's own content unexpectedly.
- Removed unused import `from time import sleep` (shadowed by `import time`).
- Replaced `sys.exit(main())` with `main()` in the `__main__` guard; `sys`
  import removed accordingly.
- Removed commented-out dead code from the demo loop in `main()`.

#### `main.py`
- Removed unused `import ssd1306` (the driver is loaded transitively through
  `oled_display`).
- Removed unused `from time import sleep` import.
- Removed commented-out dead code.

### Removed
- Dead commented-out code across `main.py`, `oled_display.py`, and
  `get_wifi_connection.py`.
