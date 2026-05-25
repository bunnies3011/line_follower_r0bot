"""
wifi_comm.py – WiFi UDP receiver cho ESP32.

ESP32 kết nối WiFi (STA mode) và lắng nghe UDP packets chứa action từ PC.
"""

import network
import socket


class WiFiComm:
    """WiFi UDP receiver.

    Workflow:
      1. Kết nối WiFi network (STA mode)
      2. Bind UDP socket trên port 8888
      3. Non-blocking recvfrom() để nhận action (1 byte: 0/1/2)
    """

    def __init__(self, ssid: str, password: str, port: int):
        """
        Args:
            ssid: WiFi SSID
            password: WiFi password
            port: UDP port để lắng nghe (default: 8888)
        """
        self.ssid = ssid
        self.password = password
        self.port = port
        self.sock = None
        self.wlan = None

    def connect(self) -> str:
        """Kết nối WiFi và bind UDP socket.

        Returns:
            IP address của ESP32 (string)

        Raises:
            RuntimeError: Nếu không kết nối được WiFi
        """
        # Activate WiFi interface (STA mode)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        # Connect to WiFi
        print(f"Connecting to WiFi: {self.ssid}...")
        self.wlan.connect(self.ssid, self.password)

        # Wait for connection (timeout ~10s)
        max_wait = 10
        while max_wait > 0:
            if self.wlan.isconnected():
                break
            max_wait -= 1
            import time
            time.sleep(1)

        if not self.wlan.isconnected():
            raise RuntimeError(f"Failed to connect to WiFi: {self.ssid}")

        # Get IP address
        ip = self.wlan.ifconfig()[0]
        print(f"WiFi connected! IP: {ip}")

        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.setblocking(False)  # Non-blocking mode

        print(f"UDP socket listening on port {self.port}")

        return ip

    def read_action(self):
        """Non-blocking read từ UDP socket.

        Returns:
            int: action (0, 1, 2) nếu nhận được packet
            None: nếu không có data (non-blocking)

        Note:
            Chỉ đọc byte đầu tiên của packet.
        """
        try:
            data, addr = self.sock.recvfrom(1)  # Read 1 byte
            if len(data) > 0:
                return data[0]  # Return action as int
        except OSError:
            # No data available (non-blocking)
            pass

        return None

    def close(self):
        """Đóng socket và disconnect WiFi."""
        if self.sock:
            self.sock.close()
        if self.wlan:
            self.wlan.disconnect()
            self.wlan.active(False)
