# Avoid Car — Hardware-in-the-Loop Simulation

Xe tránh vật cản điều khiển qua WiFi: PC chạy DQN simulation → gửi action qua UDP → ESP32 điều khiển motor.

## Architecture

```
┌─────────────────────────────────────┐
│  PC (Simulation + DQN)              │
│  - Load map, obstacles              │
│  - DQN inference → action (0/1/2)   │
│  - UDP send action → ESP32          │
└──────────────┬──────────────────────┘
               │ WiFi UDP
               │ Port 8888
┌──────────────▼──────────────────────┐
│  ESP32 (avoid_car firmware)         │
│  - Receive action via UDP           │
│  - Map action → motor speeds        │
│  - Drive motors (TB6612)            │
└─────────────────────────────────────┘
```

## File Structure

```
avoid_car/
├── esp32/                    # Firmware cho ESP32
│   ├── config.py            # Motor pins + WiFi + speeds
│   ├── motor.py             # Motor driver (TB6612FNQ)
│   ├── action_driver.py     # Map action → motor speeds
│   ├── wifi_comm.py         # WiFi + UDP receiver
│   └── main.py              # Entry point
│
├── pc/                       # PC-side code
│   └── sender.py            # Chạy simulation + gửi action
│
├── simulation_repo/          # DQN simulation (existing)
└── workflow/                 # Documentation
```

## Setup

### 1. ESP32 Firmware

#### a. Cấu hình WiFi

Mở `esp32/config.py` và điền WiFi credentials:

```python
WIFI_SSID = "your_wifi_name"
WIFI_PASS = "your_wifi_password"
```

#### b. Flash firmware lên ESP32

```bash
# Copy toàn bộ folder esp32/ lên ESP32 (dùng ampy, rshell, hoặc Thonny)
ampy --port /dev/ttyUSB0 put esp32/config.py
ampy --port /dev/ttyUSB0 put esp32/motor.py
ampy --port /dev/ttyUSB0 put esp32/action_driver.py
ampy --port /dev/ttyUSB0 put esp32/wifi_comm.py
ampy --port /dev/ttyUSB0 put esp32/main.py
```

#### c. Chạy firmware

```bash
# Connect serial monitor
screen /dev/ttyUSB0 115200

# Hoặc dùng Thonny: Run → Run current script
```

ESP32 sẽ in ra IP address sau khi connect WiFi:

```
==================================================
Avoid Car Firmware — ESP32
==================================================

[1/4] Initializing motor driver...
[2/4] Initializing action driver...
[3/4] Initializing emergency stop button...
[4/4] Connecting WiFi...
Connecting to WiFi: your_wifi_name...
WiFi connected! IP: 192.168.1.123
UDP socket listening on port 8888

==================================================
✓ Ready! Listening on 192.168.1.123:8888
==================================================

Waiting for actions from PC...
Press button (GPIO23) for emergency stop.
```

**Note lại IP address này** (ví dụ: `192.168.1.123`)

---

### 2. PC Sender

#### a. Cấu hình ESP32 IP

Mở `pc/sender.py` và điền IP address của ESP32:

```python
ESP32_IP = "192.168.1.123"  # IP từ bước 1c
```

#### b. Chạy sender

```bash
cd avoid_car/pc
python sender.py
```

Output:

```
============================================================
Avoid Car — PC Sender
============================================================

✓ UDP socket created
Sending actions to 192.168.1.123:8888

============================================================
DEMO MODE: Sending test sequence
============================================================
Sequence: FORWARD → LEFT → RIGHT → FORWARD (loop)
Press Ctrl+C to stop

[0001] Sent: FORWARD (0)
[0002] Sent: FORWARD (0)
[0003] Sent: FORWARD (0)
[0004] Sent: TURN_LEFT (1)
...
```

---

## Testing

### Test 1: WiFi Connection

✅ ESP32 kết nối WiFi và in ra IP address

### Test 2: UDP Echo

✅ PC gửi action → ESP32 nhận và print ra Serial monitor

### Test 3: Motor Test (kê xe lên)

- Gửi `FORWARD (0)` → 2 bánh quay đều với tốc độ 170
- Gửi `TURN_LEFT (1)` → bánh phải nhanh (170), bánh trái chậm (50)
- Gửi `TURN_RIGHT (2)` → bánh trái nhanh (170), bánh phải chậm (50)

### Test 4: Sequence Test (mặt phẳng)

Chạy test sequence: `[FORWARD, FORWARD, LEFT, LEFT, FORWARD, RIGHT, RIGHT, FORWARD]`

Xe nên di chuyển: thẳng → rẽ trái → thẳng → rẽ phải → thẳng

---

## Integration với DQN Simulation

Hiện tại `pc/sender.py` chạy ở **demo mode** với test sequence cố định.

Để integrate với DQN simulation thực tế:

1. Load environment từ `simulation_repo/car/`
2. Load trained DQN agent từ checkpoint
3. Replace demo loop bằng actual inference:

```python
# In send_action_loop():
state = env.reset()

while True:
    # DQN inference
    state_tensor = torch.FloatTensor(state).unsqueeze(0)
    action = agent.select_action(state_tensor, epsilon=0.0)
    
    # Send to ESP32
    sock.sendto(bytes([action]), (esp32_ip, udp_port))
    
    # Step simulation
    state, reward, done, info = env.step(action)
    
    if done:
        state = env.reset()
    
    time.sleep(DT)
```

---

## Troubleshooting

### ESP32 không connect được WiFi

- Check SSID/password trong `config.py`
- Check WiFi network có hoạt động không
- ESP32 chỉ hỗ trợ 2.4GHz WiFi (không hỗ trợ 5GHz)

### PC không gửi được UDP

- Check ESP32 IP address đúng chưa
- Check PC và ESP32 cùng network không
- Test ping: `ping 192.168.1.123`

### Motor không chạy

- Check wiring: motor pins giống `src_code/config.py`
- Check STBY pin nối 3.3V
- Check battery đủ điện

### Xe chạy sai hướng

- Điều chỉnh logic trong `action_driver.py`:
  - Swap `right` và `left` trong `speed_run()`
  - Hoặc đổi `SPEED_TURN_FAST` và `SPEED_TURN_SLOW`

---

## Safety Features

1. **UDP Timeout**: Nếu không nhận action trong 500ms → stop motor
2. **Emergency Stop Button**: GPIO23 (active LOW) → stop motor ngay lập tức
3. **Non-blocking UDP**: Main loop không bị block nếu không có data

---

## Next Steps

- [ ] Tune `SPEED_TURN_SLOW` để xe rẽ mượt hơn
- [ ] Integrate với DQN simulation thực tế
- [ ] Add visualization: plot trajectory của xe thực vs simulation
- [ ] Add telemetry: ESP32 gửi ngược lại position/speed về PC
