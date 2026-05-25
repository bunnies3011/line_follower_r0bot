"""
config.py – Cấu hình cho avoid_car firmware (ESP32).

Xe nhận action qua WiFi UDP từ PC simulation và điều khiển motor.
Motor pins giống src_code/config.py.
"""

# ======================== MOTOR DRIVER (TB6612FNQ) ========================
# Motor A (Left)
PIN_PWMA = 18   # D18 → PWMA  – Tốc độ Motor A
PIN_AIN1 = 21   # D21 → AIN1  – Chiều quay Motor A
PIN_AIN2 = 19   # D19 → AIN2  – Chiều quay Motor A

# Motor B (Right)
PIN_PWMB = 5    # D5  → PWMB  – Tốc độ Motor B
PIN_BIN1 = 15   # D15 → BIN1  – Chiều quay Motor B
PIN_BIN2 = 2    # D2  → BIN2  – Chiều quay Motor B (strapping pin!)

# STBY nối cứng 3v3 → driver luôn sẵn sàng, không cần GPIO

# PWM config
PWM_FREQ = 1000     # Hz – tần số PWM cho motor
PWM_MAX_DUTY = 1023 # ESP32 MicroPython duty range: 0–1023

# ======================== SPEED ========================
# Speeds match simulation ratio và src_code/config.py
SPEED_SCALE = 255       # Arduino speed range max
SPEED_FORWARD = 170     # Chạy thẳng (giống SPEED_DEFAULT của line follower)
SPEED_TURN_FAST = 170   # Bánh ngoài khi rẽ
SPEED_TURN_SLOW = 50    # Bánh trong khi rẽ

# ======================== WIFI ========================
# User cần điền SSID và password của WiFi network
WIFI_SSID = "YOUR_SSID"
WIFI_PASS = "YOUR_PASSWORD"
UDP_PORT = 8888

# ======================== TIMING & SAFETY ========================
LOOP_DELAY_MS = 100     # Match simulation dt=0.1s (100ms/step)
UDP_TIMEOUT_MS = 500    # Stop motor nếu không nhận action trong 500ms

# ======================== BUTTON ========================
PIN_BUTTON = 23  # D23 – Emergency stop button
