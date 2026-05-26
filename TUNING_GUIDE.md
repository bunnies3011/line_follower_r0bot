# Hướng dẫn Tuning - Line Follower Car

## 📋 Tổng quan các cải tiến

Code đã được nâng cấp với 5 tính năng mới để xe chạy êm hơn và phản ứng kịp khi quay góc:

1. **Motor Ramping** - Tốc độ motor tăng/giảm dần
2. **Sensor Filtering** - Lọc nhiễu từ cảm biến
3. **Steering Smoothing** - Làm mượt góc lái
4. **Adaptive Speed** - Tự động giảm tốc khi vào cua
5. **Loop Timing** - Tăng tần số sampling

---

## 🎛️ Các tham số trong `config.py`

### 1. Motor Ramping
```python
MOTOR_RAMP_RATE = 25  # Tốc độ thay đổi tối đa mỗi vòng (0-255)
```

**Tác dụng:** Giới hạn tốc độ motor thay đổi đột ngột, giảm giật.

**Tuning:**
- **Giá trị thấp (10-15):** Xe chạy rất êm nhưng phản ứng chậm
- **Giá trị trung bình (20-30):** Cân bằng tốt ✅
- **Giá trị cao (40-50):** Phản ứng nhanh nhưng vẫn giật

**Triệu chứng cần điều chỉnh:**
- Xe giật khi tăng/giảm tốc → Giảm RAMP_RATE
- Xe phản ứng chậm khi vào cua → Tăng RAMP_RATE

---

### 2. Sensor Filtering
```python
SENSOR_FILTER_ALPHA = 0.4  # 0.0 = không filter, 1.0 = không smoothing
```

**Tác dụng:** Lọc nhiễu ADC bằng exponential moving average.

**Tuning:**
- **Alpha thấp (0.2-0.3):** Lọc nhiễu tốt nhưng phản ứng chậm
- **Alpha trung bình (0.4-0.5):** Cân bằng tốt ✅
- **Alpha cao (0.6-0.8):** Phản ứng nhanh nhưng nhiễu nhiều

**Triệu chứng cần điều chỉnh:**
- Xe dao động liên tục trên đường thẳng → Giảm ALPHA (lọc nhiều hơn)
- Xe phản ứng chậm với line → Tăng ALPHA

---

### 3. Steering Smoothing
```python
STEERING_SMOOTH_ALPHA = 0.6  # Alpha cho steering smoothing
STEERING_SMOOTH_ADAPTIVE = True  # Tăng alpha khi error lớn
```

**Tác dụng:** Làm mượt góc lái, giảm dao động bánh xe.

**Tuning:**
- **Alpha thấp (0.3-0.4):** Góc lái rất mượt nhưng phản ứng chậm
- **Alpha trung bình (0.5-0.7):** Cân bằng tốt ✅
- **Alpha cao (0.8-0.9):** Phản ứng nhanh nhưng giật

**ADAPTIVE = True:** Tự động tăng alpha khi error lớn (cua gắt) để phản ứng nhanh hơn.

**Triệu chứng cần điều chỉnh:**
- Bánh xe giật liên tục → Giảm ALPHA
- Xe không kịp quay khi vào cua gắt → Tăng ALPHA hoặc bật ADAPTIVE

---

### 4. Adaptive Speed Control
```python
ADAPTIVE_SPEED_ENABLED = True  # Bật/tắt adaptive speed
ADAPTIVE_SPEED_MIN_FACTOR = 0.6  # Giảm tốc tối đa xuống 60%
ADAPTIVE_SPEED_CURVE_THRESHOLD = 50  # Ngưỡng servo_pwm để bắt đầu giảm tốc
```

**Tác dụng:** Tự động giảm tốc độ khi góc lái lớn (cua gắt).

**Tuning:**
- **MIN_FACTOR = 0.5:** Giảm tốc mạnh (xuống 50%) - an toàn hơn
- **MIN_FACTOR = 0.7:** Giảm tốc nhẹ (xuống 70%) - nhanh hơn ✅
- **MIN_FACTOR = 0.9:** Gần như không giảm tốc

- **THRESHOLD = 30:** Bắt đầu giảm tốc sớm (cua nhẹ cũng giảm)
- **THRESHOLD = 50:** Cân bằng ✅
- **THRESHOLD = 70:** Chỉ giảm tốc khi cua rất gắt

**Triệu chứng cần điều chỉnh:**
- Xe trượt/văng khi vào cua → Giảm MIN_FACTOR hoặc THRESHOLD
- Xe chạy quá chậm trên đường cong → Tăng MIN_FACTOR hoặc THRESHOLD
- Muốn tắt tính năng → Set ENABLED = False

---

### 5. Loop Timing
```python
LOOP_DELAY_MS = 3  # ~333 Hz main loop
```

**Tác dụng:** Tăng tần số sampling để phản ứng nhanh hơn.

**Tuning:**
- **5ms (200 Hz):** Giá trị cũ, ổn định
- **3ms (333 Hz):** Phản ứng nhanh hơn ✅
- **2ms (500 Hz):** Rất nhanh nhưng có thể quá tải CPU
- **1ms (1000 Hz):** Không khuyến nghị cho ESP32

**Lưu ý:** Giá trị quá nhỏ có thể làm ESP32 quá tải.

---

## 🔧 Quy trình Tuning

### Bước 1: Test với giá trị mặc định
1. Upload code lên ESP32
2. Chạy xe trên track
3. Quan sát hành vi:
   - Xe có giật không?
   - Xe có dao động trên đường thẳng không?
   - Xe có kịp quay khi vào cua không?
   - Xe có trượt/văng khi vào cua gắt không?

### Bước 2: Điều chỉnh từng tham số
**Thứ tự ưu tiên:**

1. **MOTOR_RAMP_RATE** - Nếu xe giật khi tăng/giảm tốc
2. **ADAPTIVE_SPEED_MIN_FACTOR** - Nếu xe trượt khi vào cua
3. **SENSOR_FILTER_ALPHA** - Nếu xe dao động trên đường thẳng
4. **STEERING_SMOOTH_ALPHA** - Nếu bánh xe giật
5. **LOOP_DELAY_MS** - Nếu cần phản ứng nhanh hơn

### Bước 3: Fine-tuning
- Chỉ thay đổi 1 tham số mỗi lần
- Thay đổi từng bước nhỏ (±5 hoặc ±0.1)
- Test sau mỗi thay đổi
- Ghi chú kết quả

---

## 📊 Bảng tham số khuyến nghị

| Loại track | RAMP_RATE | FILTER_ALPHA | SMOOTH_ALPHA | MIN_FACTOR | THRESHOLD |
|------------|-----------|--------------|--------------|------------|-----------|
| **Đường thẳng nhiều** | 30 | 0.5 | 0.7 | 0.8 | 60 |
| **Cân bằng** ✅ | 25 | 0.4 | 0.6 | 0.6 | 50 |
| **Cua gắt nhiều** | 20 | 0.3 | 0.5 | 0.5 | 40 |
| **Track xấu/nhiễu** | 20 | 0.3 | 0.5 | 0.6 | 50 |

---

## 🚨 Xử lý sự cố

### Xe giật liên tục
- Giảm `MOTOR_RAMP_RATE` xuống 15-20
- Giảm `STEERING_SMOOTH_ALPHA` xuống 0.4-0.5

### Xe dao động trên đường thẳng
- Giảm `SENSOR_FILTER_ALPHA` xuống 0.3
- Kiểm tra lại PID (KP, KD)

### Xe không kịp quay khi vào cua
- Tăng `STEERING_SMOOTH_ALPHA` lên 0.7-0.8
- Bật `STEERING_SMOOTH_ADAPTIVE = True`
- Tăng `MOTOR_RAMP_RATE` lên 30-35

### Xe trượt/văng khi vào cua gắt
- Giảm `ADAPTIVE_SPEED_MIN_FACTOR` xuống 0.5
- Giảm `ADAPTIVE_SPEED_CURVE_THRESHOLD` xuống 40
- Giảm `SPEED_DEFAULT` trong config

### Xe phản ứng chậm tổng thể
- Giảm `LOOP_DELAY_MS` xuống 2ms
- Tăng tất cả ALPHA lên 0.1-0.2
- Tăng `MOTOR_RAMP_RATE` lên 30-40

---

## 💡 Tips nâng cao

### 1. Tắt từng tính năng để debug
```python
# Tắt adaptive speed
ADAPTIVE_SPEED_ENABLED = False

# Tắt steering smoothing (set alpha = 1.0)
STEERING_SMOOTH_ALPHA = 1.0

# Tắt sensor filtering (set alpha = 1.0)
SENSOR_FILTER_ALPHA = 1.0

# Tắt motor ramping (set rate rất cao)
MOTOR_RAMP_RATE = 255
```

### 2. So sánh với code cũ
- Backup code cũ
- Test cả 2 phiên bản trên cùng track
- So sánh thời gian hoàn thành

### 3. Log dữ liệu (nếu cần)
Thêm print trong `fsm.py`:
```python
print(f"Speed: {adjusted_speed}, Angle: {angle}, Sensor: {self._bitmask:08b}")
```

---

## 📝 Ghi chú

- Tất cả tính năng đều có thể tắt nếu không cần
- Giá trị mặc định đã được tune cho track cân bằng
- Nếu xe chạy tốt với code cũ, có thể giữ nguyên PID và chỉ bật motor ramping
- Pylance errors về `time.ticks_ms()` là bình thường (MicroPython API)

---

**Chúc bạn tuning thành công! 🏎️💨**
