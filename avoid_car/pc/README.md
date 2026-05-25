# PC Sender — Avoid Car

Script Python chạy trên PC để gửi action qua UDP → ESP32.

## Files

- `sender.py` — Main script: simulation + UDP sender

## Quick Start

### 1. Cấu hình ESP32 IP

Sau khi ESP32 connect WiFi và in ra IP (ví dụ: `192.168.1.123`), mở `sender.py` và điền:

```python
ESP32_IP = "192.168.1.123"  # IP từ ESP32
```

### 2. Chạy demo mode

```bash
cd avoid_car/pc
python sender.py
```

Demo mode sẽ gửi test sequence:
```
FORWARD → FORWARD → FORWARD → LEFT → LEFT → FORWARD → RIGHT → RIGHT → FORWARD
```

### 3. Verify

Check Serial monitor của ESP32, nên thấy:

```
[10] Action: FORWARD (0)
[20] Action: TURN_LEFT (1)
[30] Action: TURN_RIGHT (2)
...
```

## Integration với DQN

Để integrate với simulation thực tế, sửa `send_action_loop()`:

```python
def send_action_loop(esp32_ip: str, udp_port: int, agent: DQNAgent):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Load environment
    from apps.simulation.main import create_env
    env = create_env()
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
        
        time.sleep(0.1)  # Match dt=0.1s
```

## Dependencies

```bash
# Install PyTorch (nếu chưa có)
pip install torch

# Simulation repo dependencies
cd ../simulation_repo/car
pip install -e .
```

## Troubleshooting

### Cannot import simulation modules

Check `REPO_ROOT` path trong `sender.py`:

```python
REPO_ROOT = Path(__file__).parent.parent / "simulation_repo/car"
```

### UDP không gửi được

- Check ESP32 IP đúng chưa
- Check PC và ESP32 cùng network
- Test ping: `ping 192.168.1.123`
- Check firewall không block UDP port 8888

### Model không load được

Check path trong `sender.py`:

```python
MODEL_PATH = REPO_ROOT / "export/model"
```

Và verify checkpoint file tồn tại:
```bash
ls ../simulation_repo/car/export/model/checkpoint.pth
```
