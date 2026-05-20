"""
fsm.py – Finite State Machine điều hướng xe dò line.

FSM dựa trên logic loop() trong Arduino example_main.ino,
chuyển sang dùng time.ticks_ms() thay vì biến cnt trong ISR.

States:
  10 – Khởi động (chạy thẳng chậm)
  11 – Chạy dò line (PD control)
  12 – Phân loại mất line
  21/22 – Rẽ phải 2 bước
  31/32 – Rẽ trái 2 bước
  50 – Xử lý ngã tư
  100 – Dừng
"""

import time

from config import (
    MASK_CENTER,
    MASK_INTERSECTION,
    MASK_LEFT_EDGE,
    MASK_RIGHT_EDGE,
    REMEMBER_TIMEOUT,
    SPEED_DEFAULT,
    SPEED_REVERSE,
    SPEED_SCALE,
    SPEED_START,
    STARTUP_TICKS,
)


# ======================== STATES ========================
STATE_STARTUP = 10
STATE_FOLLOW = 11
STATE_LOST_LINE = 12
STATE_TURN_RIGHT_1 = 21
STATE_TURN_RIGHT_2 = 22
STATE_TURN_LEFT_1 = 31
STATE_TURN_LEFT_2 = 32
STATE_INTERSECTION = 50
STATE_STOP = 100


class LineFollowerFSM:
    """FSM điều hướng xe dò line.

    Sử dụng sensor bitmask và PD controller để điều khiển motor.
    Logic chuyển state giữ nguyên từ code Arduino.
    """

    def __init__(self, motor, sensor_array, controller, calibration):
        """
        Args:
            motor: MotorDriver instance.
            sensor_array: SensorArray instance.
            controller: PDController instance.
            calibration: Calibration instance.
        """
        self._motor = motor
        self._sensor = sensor_array
        self._controller = controller
        self._calibration = calibration

        self.state = STATE_STARTUP
        self.speed = SPEED_DEFAULT
        self.cross_count = 0
        self.remember_line = 0

        self._state_start_ms = time.ticks_ms()
        self._remember_ms = time.ticks_ms()

        # Sensor data (cập nhật mỗi vòng)
        self._bitmask = 0
        self._raw = [0] * 8
        self._normalized = [0] * 8
        self._servo_pwm = 0

    def update(self):
        """Gọi mỗi vòng lặp chính.

        1. Đọc sensor
        2. Tính PD
        3. Chạy state machine
        """
        # Đọc sensor
        self._raw = self._sensor.read_raw()
        self._bitmask = self._sensor.read_bitmask(
            self._raw, self._calibration.compare_value
        )
        self._normalized = self._sensor.normalize(
            self._raw,
            self._calibration.black_value,
            self._calibration.white_value,
        )

        # Tính PD controller
        self._servo_pwm = self._controller.compute(self._normalized)

        # Chạy FSM
        self._run_state()

    def _run_state(self):
        """Xử lý state machine – logic giống loop() Arduino."""
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self._state_start_ms)

        if self.state == STATE_STARTUP:
            # State 10: Chạy thẳng chậm, chờ hết thời gian khởi động
            if elapsed >= STARTUP_TICKS:
                self._change_state(STATE_FOLLOW)
                return
            self._follow_line(SPEED_START)

        elif self.state == STATE_FOLLOW:
            # State 11: Chạy dò line chính

            # Phát hiện ngã tư (2 cảm biến ngoài cùng cùng sáng)
            if self._mask(MASK_INTERSECTION) == MASK_INTERSECTION:
                self.cross_count += 1
                self._change_state(STATE_INTERSECTION)
                return

            # Ghi nhớ hướng line (để xử lý khi mất line)
            if self._mask(MASK_RIGHT_EDGE):
                self.remember_line = 1
                self._remember_ms = now
            elif self._mask(MASK_LEFT_EDGE):
                self.remember_line = -1
                self._remember_ms = now

            # Timeout xóa remember
            if time.ticks_diff(now, self._remember_ms) > REMEMBER_TIMEOUT:
                self.remember_line = 0

            # Mất line
            if self._bitmask == 0x00:
                if self.remember_line != 0:
                    self._change_state(STATE_LOST_LINE)
                else:
                    self._motor.stop()
                return

            # Chạy bình thường với PD control
            self._follow_line(self.speed)

        elif self.state == STATE_LOST_LINE:
            # State 12: Phân loại mất line → rẽ theo hướng nhớ
            if self.remember_line == 1:
                self._motor.speed_run(self.speed, SPEED_REVERSE)
                self._change_state(STATE_TURN_RIGHT_1)
            elif self.remember_line == -1:
                self._motor.speed_run(SPEED_REVERSE, self.speed)
                self._change_state(STATE_TURN_LEFT_1)
            else:
                self._change_state(STATE_FOLLOW)

        elif self.state == STATE_TURN_RIGHT_1:
            # State 21: Quay phải bước 1 – chờ thấy cạnh phải
            self._motor.speed_run(self.speed, SPEED_REVERSE)
            if self._mask(MASK_RIGHT_EDGE):
                self._motor.speed_run(self.speed, self.speed // 2)
                self._change_state(STATE_TURN_RIGHT_2)

        elif self.state == STATE_TURN_RIGHT_2:
            # State 22: Quay phải bước 2 – chờ line về giữa
            self._motor.speed_run(self.speed, self.speed // 2)
            if self._mask(MASK_CENTER):
                self._change_state(STATE_FOLLOW)

        elif self.state == STATE_TURN_LEFT_1:
            # State 31: Quay trái bước 1 – chờ thấy cạnh trái
            self._motor.speed_run(SPEED_REVERSE, self.speed)
            if self._mask(MASK_LEFT_EDGE):
                self._motor.speed_run(self.speed // 2, self.speed)
                self._change_state(STATE_TURN_LEFT_2)

        elif self.state == STATE_TURN_LEFT_2:
            # State 32: Quay trái bước 2 – chờ line về giữa
            self._motor.speed_run(self.speed // 2, self.speed)
            if self._mask(MASK_CENTER):
                self._change_state(STATE_FOLLOW)

        elif self.state == STATE_INTERSECTION:
            # State 50: Xử lý ngã tư (logic từ Arduino)
            self._handle_intersection()

        elif self.state == STATE_STOP:
            # State 100: Dừng
            self._motor.stop()

    def _handle_intersection(self):
        """Xử lý ngã tư dựa trên cross_count.

        Arduino gốc: ngã tư 1 → rẽ phải, ngã tư 2 → rẽ trái.
        Có thể mở rộng cho nhiều ngã tư hơn.
        """
        if self.cross_count == 1:
            # Rẽ phải: motor phải chậm
            self._motor.speed_run(self.speed, self.speed // 6)
            if self._mask(MASK_CENTER):
                self._change_state(STATE_FOLLOW)

        elif self.cross_count == 2:
            # Rẽ trái: motor trái chậm
            self._motor.speed_run(self.speed // 6, self.speed)
            if self._mask(MASK_CENTER):
                self._change_state(STATE_FOLLOW)

        else:
            # Ngã tư thứ 3+: đi thẳng (có thể tùy chỉnh)
            self._change_state(STATE_FOLLOW)

    def _follow_line(self, speed):
        """Chạy dò line dùng PD controller.

        Thay thế hàm runforwardline() với switch(sensor) 25+ cases
        trong code Arduino. Dùng servo_pwm trực tiếp từ PD controller.

        Args:
            speed: Tốc độ cơ bản (0–255).
        """
        if self._bitmask == 0x00:
            # Mất line hoàn toàn → dừng
            self._motor.stop()
            return

        angle = self._servo_pwm
        self._handle_and_speed(angle, speed)

    def _handle_and_speed(self, angle, speed):
        """Chia tốc độ 2 bánh dựa trên góc hiệu chỉnh.

        Fix lỗi clamp trong code Arduino gốc:
        Dùng constrain cho từng bánh thay vì sửa speed chung.

        Args:
            angle: Giá trị hiệu chỉnh từ PD controller.
            speed: Tốc độ cơ bản.
        """
        speed_left = speed - angle
        speed_right = speed + angle

        # Constrain (fix: code gốc có logic clamp sai)
        speed_left = max(-SPEED_SCALE, min(SPEED_SCALE, speed_left))
        speed_right = max(-SPEED_SCALE, min(SPEED_SCALE, speed_right))

        self._motor.speed_run(speed_right, speed_left)

    def _mask(self, mask):
        """Kiểm tra bitmask sensor (giống sensorMask() Arduino).

        Args:
            mask: Bitmask cần kiểm tra.

        Returns:
            int: Kết quả AND giữa sensor bitmask và mask.
        """
        return self._bitmask & mask

    def _change_state(self, new_state):
        """Chuyển state và reset timer."""
        self.state = new_state
        self._state_start_ms = time.ticks_ms()
