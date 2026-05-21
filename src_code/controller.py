"""
controller.py – Bộ điều khiển PD cho xe dò line.

Tính vị trí line bằng weighted average, sau đó áp dụng PD control
để tạo giá trị hiệu chỉnh tốc độ (servo_pwm).

Fixes so với code Arduino gốc:
  - Tránh chia cho 0 khi sum = 0
  - Dùng constrain thay vì set 0 khi vượt ngưỡng
"""

from config import KD, KP, NUM_SENSORS, PD_CENTER, PD_CLAMP, PD_DIVIDER


class PDController:
    """Bộ điều khiển Proportional-Derivative cho line following.

    Quy trình tính:
    1. Weighted average: avg = Σ(sensorPID[j] * j * 1000) / Σ(sensorPID[j])
    2. Error: i = avg - PD_CENTER (= 0 khi line ở giữa)
    3. P = KP * error
    4. D = KD * (lastPos - error)  → giảm dao động
    5. servo_pwm = (P - D) / PD_DIVIDER
    """

    def __init__(self):
        self._last_pos = 0
        self.servo_pwm = 0

    def compute(self, normalized_values):
        """Tính servo_pwm từ giá trị sensor đã chuẩn hóa (0–1000).

        Args:
            normalized_values: list[int] – 8 giá trị chuẩn hóa.
                Index 0 = sensor 8 (trái), index 7 = sensor 1 (phải).

        Returns:
            int: Giá trị hiệu chỉnh tốc độ (servo_pwm).
                 Âm = line lệch trái.
                 Dương = line lệch phải.
        """
        avg = 0
        total = 0

        for j in range(NUM_SENSORS):
            avg += normalized_values[j] * (j * 1000)
            total += normalized_values[j]

        # Fix chia cho 0: giữ vị trí cuối nếu mất tín hiệu
        if total > 0:
            error = avg // total - PD_CENTER
        else:
            error = self._last_pos

        # PD calculation
        p_term = KP * error
        d_term = KD * (self._last_pos - error)
        result = p_term - d_term

        # Constrain (fix: code gốc set 0 khi < -4000, gây giật)
        if result > PD_CLAMP:
            result = PD_CLAMP
        elif result < -PD_CLAMP:
            result = -PD_CLAMP

        self.servo_pwm = result // PD_DIVIDER
        self._last_pos = error

        return self.servo_pwm

    def reset(self):
        """Reset trạng thái controller (gọi khi bắt đầu chạy)."""
        self._last_pos = 0
        self.servo_pwm = 0
