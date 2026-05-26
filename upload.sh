#!/bin/bash

echo "=========================================="
echo "  Upload Line Follower Code to ESP32"
echo "=========================================="
echo ""

# Kiểm tra mpremote
if ! command -v mpremote &> /dev/null; then
    echo "❌ mpremote not found!"
    echo "   Install: pip install mpremote"
    exit 1
fi

echo "=== Step 1: Cleaning old files ==="
mpremote rm :config.py 2>/dev/null || true
mpremote rm :motor.py 2>/dev/null || true
mpremote rm :sensor.py 2>/dev/null || true
mpremote rm :controller.py 2>/dev/null || true
mpremote rm :fsm.py 2>/dev/null || true
mpremote rm :main.py 2>/dev/null || true
mpremote rm :config.pyc 2>/dev/null || true
mpremote rm :motor.pyc 2>/dev/null || true
mpremote rm :sensor.pyc 2>/dev/null || true
mpremote rm :controller.pyc 2>/dev/null || true
mpremote rm :fsm.pyc 2>/dev/null || true
echo "✓ Old files cleaned"
echo ""

echo "=== Step 2: Uploading new files ==="
echo "  Uploading config.py..."
mpremote cp src_code/config.py :config.py
echo "  Uploading motor.py..."
mpremote cp src_code/motor.py :motor.py
echo "  Uploading sensor.py..."
mpremote cp src_code/sensor.py :sensor.py
echo "  Uploading controller.py..."
mpremote cp src_code/controller.py :controller.py
echo "  Uploading calibration.py..."
mpremote cp src_code/calibration.py :calibration.py
echo "  Uploading fsm.py..."
mpremote cp src_code/fsm.py :fsm.py
echo "  Uploading main.py..."
mpremote cp src_code/main.py :main.py
echo "✓ All files uploaded"
echo ""

echo "=== Step 3: Verifying config.py ==="
if mpremote cat :config.py | grep -q "STEERING_SMOOTH_ADAPTIVE"; then
    echo "✓ config.py contains new constants"
else
    echo "❌ config.py missing new constants!"
    echo "   Please check the file manually"
    exit 1
fi
echo ""

echo "=== Step 4: Resetting ESP32 ==="
mpremote reset
echo "✓ ESP32 reset"
echo ""

echo "=========================================="
echo "  ✓ Upload Complete!"
echo "=========================================="
echo ""
echo "The car should start running automatically."
echo "If not, check the serial output:"
echo "  mpremote run src_code/main.py"
echo ""
