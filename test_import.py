"""Test import để debug lỗi"""

print("Testing imports...")

try:
    print("1. Importing config...")
    from src_code.config import *
    print("   ✓ config OK")
except Exception as e:
    print(f"   ✗ config ERROR: {e}")

try:
    print("2. Importing motor...")
    from src_code.motor import MotorDriver
    print("   ✓ motor OK")
except Exception as e:
    print(f"   ✗ motor ERROR: {e}")

try:
    print("3. Importing sensor...")
    from src_code.sensor import SensorArray
    print("   ✓ sensor OK")
except Exception as e:
    print(f"   ✗ sensor ERROR: {e}")

try:
    print("4. Importing controller...")
    from src_code.controller import PDController
    print("   ✓ controller OK")
except Exception as e:
    print(f"   ✗ controller ERROR: {e}")

try:
    print("5. Importing fsm...")
    from src_code.fsm import LineFollowerFSM
    print("   ✓ fsm OK")
except Exception as e:
    print(f"   ✗ fsm ERROR: {e}")

print("\nAll imports tested!")
