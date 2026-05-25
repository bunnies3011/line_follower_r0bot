"""
action_driver.py – Map simulation CarAction → differential drive motor speeds.

CarAction từ simulation:
  FORWARD = 0    → cả 2 bánh chạy đều
  TURN_LEFT = 1  → bánh phải nhanh, bánh trái chậm
  TURN_RIGHT = 2 → bánh trái nhanh, bánh phải chậm
"""

from config import SPEED_FORWARD, SPEED_TURN_FAST, SPEED_TURN_SLOW


class ActionDriver:
    """Map discrete action (0, 1, 2) sang motor speeds cho differential drive.

    Convention từ src_code/motor.py:
      speed_run(right, left) — right là motor phải, left là motor trái
    """

    def __init__(self, motor_driver):
        """
        Args:
            motor_driver: Instance của MotorDriver class
        """
        self.motor = motor_driver

    def execute(self, action: int):
        """Execute action từ simulation.

        Args:
            action: 0 = FORWARD, 1 = TURN_LEFT, 2 = TURN_RIGHT

        Logic differential drive:
          - FORWARD: cả 2 bánh cùng tốc độ
          - TURN_LEFT: bánh phải nhanh hơn → xe quay trái
          - TURN_RIGHT: bánh trái nhanh hơn → xe quay phải
        """
        if action == 0:  # FORWARD
            self.motor.speed_run(right=SPEED_FORWARD, left=SPEED_FORWARD)
        elif action == 1:  # TURN_LEFT
            self.motor.speed_run(right=SPEED_TURN_FAST, left=SPEED_TURN_SLOW)
        elif action == 2:  # TURN_RIGHT
            self.motor.speed_run(right=SPEED_TURN_SLOW, left=SPEED_TURN_FAST)
        else:
            # Invalid action → stop
            self.motor.stop()

    def stop(self):
        """Dừng motor."""
        self.motor.stop()
