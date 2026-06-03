"""
config.py – Hằng số cấu hình cho xe dò line ESP32.

Pin mapping dựa trên workflow/diagram.jpeg.
Tất cả magic numbers được tập trung tại đây để dễ tune.
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

# ======================== SENSOR ARRAY (8 kênh) ========================
# Thứ tự đọc: sensor 8 (trái) → sensor 1 (phải)
# Sau shift: sensor 8 → bit 7 (MSB), sensor 1 → bit 0 (LSB)
NUM_SENSORS = 8

SENSOR_PINS = [
    26,  # Sensor 8 – D26 – ngoài cùng trái → bit 7
    25,  # Sensor 7 – D25                    → bit 6
    33,  # Sensor 6 – D33                    → bit 5
    32,  # Sensor 5 – D32                    → bit 4
    35,  # Sensor 4 – D35 (input only)       → bit 3
    34,  # Sensor 3 – D34 (input only)       → bit 2
    39,  # Sensor 2 – VN/GPIO39 (input only) → bit 1
    36,  # Sensor 1 – VP/GPIO36 (input only) – ngoài cùng phải → bit 0
]

ADC_MAX = 4095   # ESP32 ADC 12-bit
ADC_ATTEN = 3    # ADC.ATTN_11DB = 3 → full range 0–3.3V

# ======================== BUTTON ========================
PIN_BUTTON = 23  # D23 – nút Start

# ======================== PD CONTROLLER ========================
KP = 2
KD = 16
PD_DIVIDER = 30     # servoPwm = iRet / PD_DIVIDER
PD_CLAMP = 4000     # constrain iRet trong [-PD_CLAMP, PD_CLAMP]
PD_CENTER = 3500    # weighted average center: (NUM_SENSORS/2 - 0.5) * 1000

# ======================== SPEED ========================
SPEED_DEFAULT = 155     # Tốc độ chạy mặc định (scale 0–255)
SPEED_START = 130       # Tốc độ khởi động (state 10)
SPEED_REVERSE = -145    # Tốc độ quay ngược khi rẽ
SPEED_SCALE = 255       # Arduino speed range max

# ======================== TIMING ========================
LOOP_DELAY_MS = 3       # ~333 Hz main loop (giảm từ 5ms để phản ứng nhanh hơn)
STARTUP_TICKS = 500     # ms – thời gian state 10 trước khi chuyển state 11
REMEMBER_TIMEOUT = 500  # ms – giữ hướng line (tăng từ 350ms để đủ thời gian qua đoạn thẳng)
TURN_TIMEOUT_MS = 500   # ms – thoát state rẽ nếu không bắt lại line
SEARCH_TURN_TIMEOUT_MS = 380  # ms – timeout cho pha quay tìm line theo hướng gần nhất

# ======================== SMOOTHING & FILTERING ========================
# Motor ramping (acceleration limiting)
MOTOR_RAMP_RATE = 14    # Tốc độ thay đổi tối đa mỗi vòng (0-255 scale)
                        # Giá trị nhỏ = êm hơn nhưng chậm phản ứng
                        # Giá trị lớn = phản ứng nhanh nhưng giật hơn

# Sensor filtering (low-pass filter)
SENSOR_FILTER_ALPHA = 0.35  # 0.0 = không filter, 1.0 = không smoothing
                           # 0.3-0.5 = cân bằng tốt giữa nhiễu và phản ứng

# Steering smoothing
STEERING_SMOOTH_ALPHA = 0.42  # Alpha cho steering smoothing
                             # 0.5-0.7 = cân bằng tốt
STEERING_SMOOTH_ADAPTIVE = True  # Tăng alpha khi error lớn

# Adaptive speed control
ADAPTIVE_SPEED_ENABLED = True    # Bật/tắt adaptive speed
ADAPTIVE_SPEED_MIN_FACTOR = 0.5  # Giảm tốc độ tối đa xuống 50% khi quay gắt
ADAPTIVE_SPEED_CURVE_THRESHOLD = 35  # Ngưỡng servo_pwm để bắt đầu giảm tốc
SEARCH_DIRECTION_THRESHOLD = 20      # Ngưỡng servo_pwm để ghi hướng tìm line

# ======================== SENSOR MASKS ========================
MASK_INTERSECTION = 0x81    # Bit 7 + bit 0 → ngã tư
MASK_CENTER = 0x3C          # Bit 5,4,3,2 → 4 sensor giữa (mở rộng để dễ detect)
MASK_LEFT_EDGE = 0x80        # Bit 7 → line ở cạnh trái (sensor 8)
MASK_RIGHT_EDGE = 0x01       # Bit 0 → line ở cạnh phải (sensor 1)

# Sharp corner detection (góc vuông)
MASK_SHARP_LEFT = 0xF0      # 11110000 → 4 sensor trái sáng (góc vuông trái)
MASK_SHARP_RIGHT = 0x0F     # 00001111 → 4 sensor phải sáng (góc vuông phải)
MASK_SHARP_LEFT_MIN = 0xE0  # 11100000 → tối thiểu 3 sensor trái (relaxed)
MASK_SHARP_RIGHT_MIN = 0x07 # 00000111 → tối thiểu 3 sensor phải (relaxed)

# ======================== CALIBRATION ========================
CALIB_FILE = "/calibration.json"
CALIB_DEFAULT_BLACK = 4095  # Giá trị ADC mặc định cho line đen (min)
CALIB_DEFAULT_WHITE = 0     # Giá trị ADC mặc định cho nền trắng (max)
NORMALIZE_RANGE = 1000      # Chuẩn hóa sensor về 0–1000
