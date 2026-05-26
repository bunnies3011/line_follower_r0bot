"""Check if config.py has all required constants"""

try:
    from src_code.config import (
        MOTOR_RAMP_RATE,
        SENSOR_FILTER_ALPHA,
        STEERING_SMOOTH_ALPHA,
        STEERING_SMOOTH_ADAPTIVE,
        ADAPTIVE_SPEED_ENABLED,
        ADAPTIVE_SPEED_MIN_FACTOR,
        ADAPTIVE_SPEED_CURVE_THRESHOLD,
    )
    print("✓ All new constants found in config.py!")
    print(f"  MOTOR_RAMP_RATE = {MOTOR_RAMP_RATE}")
    print(f"  SENSOR_FILTER_ALPHA = {SENSOR_FILTER_ALPHA}")
    print(f"  STEERING_SMOOTH_ALPHA = {STEERING_SMOOTH_ALPHA}")
    print(f"  STEERING_SMOOTH_ADAPTIVE = {STEERING_SMOOTH_ADAPTIVE}")
    print(f"  ADAPTIVE_SPEED_ENABLED = {ADAPTIVE_SPEED_ENABLED}")
    print(f"  ADAPTIVE_SPEED_MIN_FACTOR = {ADAPTIVE_SPEED_MIN_FACTOR}")
    print(f"  ADAPTIVE_SPEED_CURVE_THRESHOLD = {ADAPTIVE_SPEED_CURVE_THRESHOLD}")
except ImportError as e:
    print(f"✗ Missing constant in config.py: {e}")
    print("\nYou need to re-upload config.py to ESP32!")
