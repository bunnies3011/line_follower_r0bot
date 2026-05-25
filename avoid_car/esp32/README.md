# ESP32 Firmware — Avoid Car

Firmware cho ESP32 nhận action qua WiFi UDP và điều khiển motor.

## Files

- `config.py` — Cấu hình motor pins, WiFi, speeds, timing
- `motor.py` — Motor driver cho TB6612FNQ (copy từ src_code)
- `action_driver.py` — Map action (0,1,2) → motor speeds
- `wifi_comm.py` — WiFi STA + UDP receiver
- `main.py` — Entry point

## Quick Start

### 1. Cấu hình WiFi

Mở `config.py` và điền:

```python
WIFI_SSID = "your_wifi_name"
WIFI_PASS = "your_wifi_password"
```

### 2. Flash lên ESP32

Dùng Thonny, ampy, hoặc rshell để copy toàn bộ files lên ESP32.

**Với Thonny:**
1. File → Open → chọn file
2. File → Save as → MicroPython device
3. Lặp lại cho tất cả files

**Với ampy:**
```bash
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put motor.py
ampy --port /dev/ttyUSB0 put action_driver.py
ampy --port /dev/ttyUSB0 put wifi_comm.py
ampy --port /dev/ttyUSB0 put main.py
```

### 3. Chạy

```bash
# Serial monitor
screen /dev/ttyUSB0 115200

# Hoặc trong Thonny: Run → Run current script (F5)
```

### 4. Note IP address

ESP32 sẽ in ra IP sau khi connect WiFi:

```
WiFi connected! IP: 192.168.1.123
✓ Ready! Listening on 192.168.1.123:8888
```

Copy IP này để điền vào `pc/sender.py`.

## Pin Mapping

Giống `src_code/config.py`:

| Component | Pin | Function |
|-----------|-----|----------|
| Motor A (Left) | D18 | PWMA (speed) |
| Motor A (Left) | D21 | AIN1 (direction) |
| Motor A (Left) | D19 | AIN2 (direction) |
| Motor B (Right) | D5 | PWMB (speed) |
| Motor B (Right) | D15 | BIN1 (direction) |
| Motor B (Right) | D2 | BIN2 (direction) |
| Emergency Stop | D23 | Button (active LOW) |

## Action Mapping

| Action | Value | Motor Speeds | Behavior |
|--------|-------|--------------|----------|
| FORWARD | 0 | right=170, left=170 | Chạy thẳng |
| TURN_LEFT | 1 | right=170, left=50 | Rẽ trái |
| TURN_RIGHT | 2 | right=50, left=170 | Rẽ phải |

## Safety Features

1. **UDP Timeout**: Stop motor nếu không nhận action trong 500ms
2. **Emergency Button**: GPIO23 (active LOW) → stop ngay
3. **Non-blocking UDP**: Main loop không bị block

## Troubleshooting

### WiFi không connect

- Check SSID/password
- ESP32 chỉ hỗ trợ 2.4GHz (không hỗ trợ 5GHz)
- Check router có bật DHCP không

### Motor không chạy

- Check wiring
- Check STBY pin nối 3.3V
- Check battery đủ điện

### Xe chạy sai hướng

Điều chỉnh trong `action_driver.py`:
- Swap `right` và `left`
- Hoặc đổi `SPEED_TURN_FAST` và `SPEED_TURN_SLOW`
