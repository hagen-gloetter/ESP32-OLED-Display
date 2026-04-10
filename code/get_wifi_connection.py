import ujson
import network
import machine
import time

_CONNECT_TIMEOUT_MS = 15000

_wifi = None


def connect_wifi():
    """Connect to the first known WiFi network found via scan.

    Reads credentials from 'secrets_wifi.json' (format: {"SSID": "password"}).
    Raises OSError if no known network is reachable or a connection times out.
    """
    global _wifi

    with open("secrets_wifi.json") as f:
        wlan_json = ujson.load(f)

    _wifi = network.WLAN(network.STA_IF)
    _wifi.active(True)
    nets = _wifi.scan()

    available_ssids = set()
    for net in nets:
        try:
            available_ssids.add(net[0].decode("utf-8"))
        except Exception:
            pass

    for ssid, pwd in wlan_json.items():
        if ssid not in available_ssids:
            continue

        print(f"Network '{ssid}' found, connecting...")
        try:
            _wifi.connect(ssid, pwd)
            start_ms = time.ticks_ms()
            while not _wifi.isconnected():
                if time.ticks_diff(time.ticks_ms(), start_ms) > _CONNECT_TIMEOUT_MS:
                    _wifi.disconnect()
                    raise OSError(f"Timeout connecting to '{ssid}'")
                machine.idle()
            print(f"Connected to '{ssid}' – IP: {_wifi.ifconfig()[0]}")
            return
        except OSError as e:
            print(f"Failed to connect to '{ssid}': {e}")
            _wifi.disconnect()

    raise OSError("No known WiFi network found or all connection attempts failed")


def ensure_wifi():
    """Reconnect to WiFi if the connection has been lost.

    Should be called periodically in the main loop.
    Raises OSError if reconnection fails (same as connect_wifi).
    """
    global _wifi
    if _wifi is None or not _wifi.isconnected():
        print("WiFi connection lost – reconnecting...")
        connect_wifi()


def get_ip():
    """Return the current IP address string, or None if not connected."""
    if _wifi is not None and _wifi.isconnected():
        return _wifi.ifconfig()[0]
    return None


def disconnect_wifi():
    """Disconnect the active WiFi connection."""
    global _wifi
    if _wifi is not None:
        print("Disconnecting WiFi...")
        _wifi.disconnect()
        _wifi = None
