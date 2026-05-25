#!/usr/bin/env python3
"""
test_udp.py – Simple UDP test script để verify connection với ESP32.

Usage:
    python test_udp.py <ESP32_IP>

Example:
    python test_udp.py 192.168.1.123
"""

import socket
import sys
import time


def test_udp_connection(esp32_ip: str, port: int = 8888):
    """Test UDP connection bằng cách gửi test sequence.

    Args:
        esp32_ip: IP address của ESP32
        port: UDP port (default: 8888)
    """
    print("=" * 60)
    print("UDP Connection Test")
    print("=" * 60)
    print(f"Target: {esp32_ip}:{port}")
    print()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("✓ UDP socket created")

    # Test sequence: FORWARD → LEFT → RIGHT → FORWARD
    test_sequence = [
        (0, "FORWARD"),
        (0, "FORWARD"),
        (1, "TURN_LEFT"),
        (1, "TURN_LEFT"),
        (2, "TURN_RIGHT"),
        (2, "TURN_RIGHT"),
        (0, "FORWARD"),
        (0, "FORWARD"),
    ]

    print("\nSending test sequence...")
    print("(Check ESP32 Serial monitor for received actions)\n")

    try:
        for i, (action, name) in enumerate(test_sequence, 1):
            # Send action
            sock.sendto(bytes([action]), (esp32_ip, port))
            print(f"[{i}/{len(test_sequence)}] Sent: {name} ({action})")
            time.sleep(0.5)  # Slower than normal for testing

        print("\n✓ Test sequence completed!")
        print("\nCheck ESP32 Serial monitor:")
        print("  - Should see action logs every 500ms")
        print("  - Motor should respond to actions (if not lifted)")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

    finally:
        sock.close()
        print("\nUDP socket closed.")

    return True


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_udp.py <ESP32_IP>")
        print("Example: python test_udp.py 192.168.1.123")
        sys.exit(1)

    esp32_ip = sys.argv[1]

    # Validate IP format (basic check)
    parts = esp32_ip.split(".")
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        print(f"Error: Invalid IP address: {esp32_ip}")
        sys.exit(1)

    # Run test
    success = test_udp_connection(esp32_ip)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
