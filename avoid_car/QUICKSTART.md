# Quick Start Guide — Avoid Car

Hướng dẫn nhanh để chạy xe tránh vật cản với WiFi control.

## 📋 Tổng quan

- **ESP32**: Nhận action qua WiFi UDP → điều khiển motor
- **PC**: Chạy simulation/DQN → gửi action qua UDP
- **Communication**: WiFi UDP port 8888
- **Actions**: 0=FORWARD, 1=TURN_LEFT, 2=TURN_RIGHT

---

## 🚀 Setup trong 5 phút

### Bước 1: Cấu hình ESP32

```bash
# 1. Mở esp32/config.py
# 2. Điền WiFi credentials:
WIFI_SSID = "your_wifi_name"
WIFI_PASS = "your_wifi_password"
```

### Bước 2: Flash ESP32

**Với Thonny:**
1. Mở Thonny IDE
2. Tools → Options → Interpreter → MicroPython (ESP32)
3. File → Open từng file trong `esp32/`
4. File → Save as → MicroPython device
5. Lặp lại cho: `config.py`, `motor.py`, `action_driver.py`, `wifi_comm.py`, `main.py`

**Với ampy:**
```bash
cd avoid_car/esp32
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put motor.py
ampy --port /dev/ttyUSB0 put action_driver.py
ampy --port /dev/ttyUSB0 put wifi_comm.py
ampy --port /dev/ttyUSB0 put main.py
```

### Bước 3: Chạy ESP32 và lấy IP

```bash
# Serial monitor
screen /dev/ttyUSB0 115200
# Hoặc dùng Thonny: Run → Run current script
```

**Output:**
```
==================================================
Avoid Car Firmware — ESP32
==================================================
...
WiFi connected! IP: 192.168.1.123  ← NOTE LẠI IP NÀY
✓ Ready! Listening on 192.168.1.123:8888
==================================================
```

### Bước 4: Test UDP từ PC

```bash
cd avoid_car/pc

# Test UDP connection
python test_udp.py 192.168.1.123

# Hoặc chạy demo mode
# (Nhớ sửa ESP32_IP trong sender.py trước)
python sender.py
```

---

## ✅ Verification Checklist

- [ ] ESP32 connect WiFi thành công
- [ ] ESP32 in ra IP address
- [ ] PC ping được ESP32: `ping 192.168.1.123`
- [ ] `test_udp.py` gửi được packets
- [ ] ESP32 Serial monitor hiển thị received actions
- [ ] Motor phản ứng với actions (nếu không kê xe lên)

---

## 🎯 Next Steps

### Demo Mode (hiện tại)
`sender.py` đang chạy test sequence cố định:
```
FORWARD → FORWARD → FORWARD → LEFT → LEFT → FORWARD → RIGHT → RIGHT → FORWARD
```

### Integration với DQN

Sửa `pc/sender.py`, function `send_action_loop()`:

```python
# Load environment và agent
from apps.simulation.main import create_env
env = create_env()
state = env.reset()

# Load trained DQN
agent = load_agent(MODEL_PATH, state_dim, action_dim)

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
    
    time.sleep(0.1)
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| ESP32 không connect WiFi | Check SSID/password, ESP32 chỉ hỗ trợ 2.4GHz |
| PC không gửi được UDP | Check IP, ping test, firewall |
| Motor không chạy | Check wiring, STBY pin nối 3.3V, battery |
| Xe chạy sai hướng | Swap `right`/`left` trong `action_driver.py` |

---

## 📚 Documentation

- `README.md` — Complete guide
- `esp32/README.md` — ESP32 firmware details
- `pc/README.md` — PC sender details
- `workflow/implementation_plan.md` — Implementation details

---

## 🛡️ Safety Features

1. **UDP Timeout**: Stop motor nếu không nhận action trong 500ms
2. **Emergency Button**: GPIO23 (active LOW) → stop ngay
3. **Non-blocking**: Main loop không bị block

---

## 📞 Support

Nếu gặp vấn đề, check:
1. Serial monitor của ESP32 (error messages)
2. WiFi connection status
3. Pin wiring theo `src_code/config.py`
4. Battery voltage đủ (>7V recommended)
