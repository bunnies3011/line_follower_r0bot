"""
motor.py – Điều khiển motor qua TB6612FNQ.

Mapping từ diagram.jpeg:
  Motor A (Left):  PWMA=D18, AIN1=D21, AIN2=D19
  Motor B (Right): PWMB=D5,  BIN1=D15, BIN2=D2
  STBY nối cứng 3v3
"""

from machine import Pin, PWM

from config import (
    MOTOR_RAMP_RATE,
    PIN_AIN1,
    PIN_AIN2,
    PIN_BIN1,
    PIN_BIN2,
    PIN_PWMA,
    PIN_PWMB,
    PWM_FREQ,
    PWM_MAX_DUTY,
    SPEED_SCALE,
)


class MotorDriver:
    """Điều khiển 2 motor DC qua TB6612FNQ driver.

    Giá trị speed theo thang 0–255 (tương thích Arduino).
    Giá trị dương = tiến, âm = lùi.
    """

    def __init__(self):
        # Motor A (Left) – direction pins
        self._ain1 = Pin(PIN_AIN1, Pin.OUT)
        self._ain2 = Pin(PIN_AIN2, Pin.OUT)
        # Motor A – PWM speed
        self._pwma = PWM(Pin(PIN_PWMA))
        self._pwma.freq(PWM_FREQ)
        self._pwma.duty(0)

        # Motor B (Right) – direction pins
        self._bin1 = Pin(PIN_BIN1, Pin.OUT)
        self._bin2 = Pin(PIN_BIN2, Pin.OUT)
        # Motor B – PWM speed
        self._pwmb = PWM(Pin(PIN_PWMB))
        self._pwmb.freq(PWM_FREQ)
        self._pwmb.duty(0)

        # Motor ramping – lưu tốc độ hiện tại để tăng/giảm dần
        self._current_speed_left = 0
        self._current_speed_right = 0

    def speed_run(self, right, left):
        """Điều khiển tốc độ và chiều quay 2 motor với ramping.

        Tham số giống code Arduino gốc:
          right: tốc độ motor phải (−255 đến +255)
          left:  tốc độ motor trái (−255 đến +255)

        Giá trị dương = tiến, âm = lùi, 0 = dừng.
        
        Ramping: Tốc độ thay đổi dần để giảm giật, cải thiện độ êm.
        """
        # Áp dụng ramping cho motor trái
        left = self._apply_ramp(left, self._current_speed_left)
        self._current_speed_left = left
        
        # Áp dụng ramping cho motor phải
        right = self._apply_ramp(right, self._current_speed_right)
        self._current_speed_right = right
        
        self._drive_left(left)
        self._drive_right(right)

    def stop(self):
        """Dừng cả 2 motor."""
        self._pwma.duty(0)
        self._pwmb.duty(0)
        self._current_speed_left = 0
        self._current_speed_right = 0

    def deinit(self):
        """Giải phóng PWM pins."""
        self._pwma.deinit()
        self._pwmb.deinit()

    def _drive_left(self, speed):
        """Điều khiển Motor A (trái).

        Logic chiều quay theo wiring thực tế:
          speed > 0: AIN1=LOW,  AIN2=HIGH, PWM=speed
          speed < 0: AIN1=HIGH, AIN2=LOW,  PWM=255+speed
          speed = 0: PWM=0
        """
        if speed > 0:
            self._ain1.value(0)
            self._ain2.value(1)
            self._pwma.duty(self._scale(speed))
        elif speed < 0:
            self._ain1.value(1)
            self._ain2.value(0)
            self._pwma.duty(self._scale(SPEED_SCALE + speed))
        else:
            self._pwma.duty(0)

    def _drive_right(self, speed):
        """Điều khiển Motor B (phải).

        Logic chiều quay theo wiring thực tế:
          speed > 0: BIN1=LOW,  BIN2=HIGH, PWM=speed
          speed < 0: BIN1=HIGH, BIN2=LOW,  PWM=255+speed
          speed = 0: PWM=0
        """
        if speed > 0:
            self._bin1.value(0)
            self._bin2.value(1)
            self._pwmb.duty(self._scale(speed))
        elif speed < 0:
            self._bin1.value(1)
            self._bin2.value(0)
            self._pwmb.duty(self._scale(SPEED_SCALE + speed))
        else:
            self._pwmb.duty(0)

    @staticmethod
    def _apply_ramp(target_speed, current_speed):
        """Áp dụng ramping để tốc độ thay đổi dần.
        
        Args:
            target_speed: Tốc độ mục tiêu (-255 đến +255)
            current_speed: Tốc độ hiện tại (-255 đến +255)
            
        Returns:
            int: Tốc độ mới sau khi áp dụng ramping
        """
        diff = target_speed - current_speed
        
        # Giới hạn thay đổi tốc độ
        if diff > MOTOR_RAMP_RATE:
            return current_speed + MOTOR_RAMP_RATE
        elif diff < -MOTOR_RAMP_RATE:
            return current_speed - MOTOR_RAMP_RATE
        else:
            return target_speed

    @staticmethod
    def _scale(value):
        """Scale giá trị từ 0–255 (Arduino) sang 0–1023 (ESP32 duty).

        Clamp để đảm bảo an toàn.
        """
        value = max(0, min(value, SPEED_SCALE))
        return int(value * PWM_MAX_DUTY // SPEED_SCALE)
