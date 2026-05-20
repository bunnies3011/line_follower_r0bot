# Sơ Đồ Kết Nối Phần Cứng - Line Follower Car

Tài liệu mô tả chi tiết các kết nối dây giữa các module phần cứng trong dự án xe dò line, dựa trên file `diagram.jpeg`.

---

## 1. ESP32 ↔ TB6612FNQ (Motor Driver)

Module điều khiển động cơ TB6612FNQ được kết nối với ESP32 để điều khiển 2 động cơ DC (Motor A và Motor B).

| ESP32 Pin | TB6612FNQ Pin | Chức năng             |
|-----------|---------------|-----------------------|
| D18       | PWMA          | Điều khiển tốc độ Motor A |
| D19       | AIN2          | Điều khiển chiều quay Motor A |
| D21       | AIN1          | Điều khiển chiều quay Motor A |
| 3v3       | STBY          | Standby (kích hoạt driver) |
| D15       | BIN1          | Điều khiển chiều quay Motor B |
| D2        | BIN2          | Điều khiển chiều quay Motor B |
| D5        | PWMB          | Điều khiển tốc độ Motor B |
| 3v3       | VCC           | Nguồn logic cho TB6612 |
| GND       | GND           | Mass chung             |

---

## 2. ESP32 ↔ Cảm Biến Dò Line (Sensor Array)

Mảng cảm biến dò line 8 kênh được kết nối với ESP32 để đọc tín hiệu vị trí của line.

| ESP32 Pin | Sensor Pin | Mô tả                |
|-----------|------------|-----------------------|
| D26       | 8          | Kênh cảm biến 8 (ngoài cùng phải) |
| D25       | 7          | Kênh cảm biến 7      |
| D33       | 6          | Kênh cảm biến 6      |
| D32       | 5          | Kênh cảm biến 5      |
| 3v3       | V          | Nguồn cấp cho cảm biến |
| D35       | 4          | Kênh cảm biến 4      |
| D34       | 3          | Kênh cảm biến 3      |
| VN        | 2          | Kênh cảm biến 2      |
| VP        | 1          | Kênh cảm biến 1 (ngoài cùng trái) |

---

## 3. ESP32 ↔ Nút Nhấn (Button)

Nút nhấn dùng để khởi động/dừng xe hoặc chuyển chế độ.

| ESP32 Pin | Button Pin | Mô tả           |
|-----------|------------|------------------|
| D23       | Signal     | Tín hiệu nút nhấn |
| 3v3       | VCC        | Nguồn cấp        |
| GND       | GND        | Mass chung        |

---

## 4. Pin 18650 ↔ LM2596 (Bộ Hạ Áp)

Pin Lithium 18650 cấp nguồn cho bộ hạ áp LM2596 để tạo nguồn ổn định cho ESP32 và các module khác.

| Pin 18650 | LM2596 Pin | Mô tả            |
|-----------|------------|-------------------|
| V+        | IN+        | Nguồn vào dương   |
| V-        | IN-        | Nguồn vào âm      |

---

## 5. LM2596 ↔ ESP32 (Cấp Nguồn)

Đầu ra của LM2596 cấp nguồn cho ESP32.

| ESP32 Pin | LM2596 Pin | Mô tả            |
|-----------|------------|-------------------|
| Vin       | OUT+       | Nguồn ra dương    |
| GND       | OUT-       | Nguồn ra âm       |

---

## 6. Pin 18650 ↔ TB6612 (Nguồn Động Cơ)

Pin 18650 cấp nguồn trực tiếp cho TB6612 để cung cấp điện cho động cơ DC.

| Pin 18650 | TB6612 Pin | Mô tả               |
|-----------|------------|----------------------|
| V+        | VM         | Nguồn động cơ dương  |
| V-        | GND        | Nguồn động cơ âm     |

---

## Sơ Đồ Tổng Quan

```
                    ┌─────────────┐
                    │  Pin 18650  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   LM2596    │          │   TB6612    │
       │  (Hạ áp)    │          │ (Motor Drv) │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              ▼                        ▼
       ┌─────────────┐          ┌───────────┐
       │   ESP32     │◄────────►│  Motor A  │
       │             │          │  Motor B  │
       └──┬─────┬────┘          └───────────┘
          │     │
          ▼     ▼
    ┌────────┐ ┌────────┐
    │ Sensor │ │ Button │
    │ Array  │ │        │
    └────────┘ └────────┘
```

---

## Lưu Ý

- **LM2596** cần được điều chỉnh điện áp đầu ra về **3.3V hoặc 5V** phù hợp với ESP32 (qua chân Vin).
- Chân **STBY** của TB6612 được nối với **3v3** để driver luôn ở trạng thái hoạt động.
- Cảm biến dò line sử dụng các chân **ADC** của ESP32 (VP, VN, D32-D35) để đọc tín hiệu analog.
- Chân **D26, D25** cũng hỗ trợ ADC trên ESP32.
