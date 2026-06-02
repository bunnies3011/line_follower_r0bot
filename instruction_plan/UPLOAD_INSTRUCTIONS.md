# Hướng dẫn Upload Code lên ESP32

## ❌ Lỗi hiện tại
```
ImportError: can't import name STEERING_SMOOTH_ADAPTIVE
```

**Nguyên nhân:** File `config.py` trên ESP32 chưa được cập nhật đầy đủ với các hằng số mới.

---

## ✅ Cách fix

### Bước 1: Xóa file cũ trên ESP32
```bash
mpremote rm :config.py
mpremote rm :motor.py
mpremote rm :sensor.py
mpremote rm :controller.py
mpremote rm :fsm.py
mpremote rm :main.py
```

### Bước 2: Upload lại tất cả file
```bash
mpremote cp src_code/config.py :config.py
mpremote cp src_code/motor.py :motor.py
mpremote cp src_code/sensor.py :sensor.py
mpremote cp src_code/controller.py :controller.py
mpremote cp src_code/calibration.py :calibration.py
mpremote cp src_code/fsm.py :fsm.py
mpremote cp src_code/main.py :main.py
```

### Bước 3: Reset ESP32
```bash
mpremote reset
```

### Bước 4: Kiểm tra
```bash
mpremote run src_code/main.py
```

---

## 🔍 Kiểm tra file config.py trên ESP32

Nếu vẫn lỗi, kiểm tra xem file config.py trên ESP32 có đầy đủ không:

```bash
mpremote cat :config.py | grep "STEERING_SMOOTH"
```

Phải thấy output:
```
STEERING_SMOOTH_ALPHA = 0.6
STEERING_SMOOTH_ADAPTIVE = True
```

---

## 📝 Lưu ý quan trọng

1. **Đường dẫn file:** Khi upload lên ESP32, file phải ở root (`:config.py`), không có thư mục `src_code/`

2. **Thứ tự upload:** Upload `config.py` TRƯỚC, sau đó mới upload các file khác

3. **Kiểm tra dung lượng:** ESP32 có thể hết bộ nhớ nếu có quá nhiều file cũ
   ```bash
   mpremote df
   ```

4. **Xóa file .pyc (nếu có):**
   ```bash
   mpremote rm :config.pyc
   mpremote rm :motor.pyc
   mpremote rm :sensor.pyc
   mpremote rm :controller.pyc
   mpremote rm :fsm.pyc
   ```

---

## 🚀 Script tự động (khuyến nghị)

Tạo file `upload.sh`:

```bash
#!/bin/bash

echo "=== Cleaning old files ==="
mpremote rm :config.py 2>/dev/null
mpremote rm :motor.py 2>/dev/null
mpremote rm :sensor.py 2>/dev/null
mpremote rm :controller.py 2>/dev/null
mpremote rm :fsm.py 2>/dev/null
mpremote rm :main.py 2>/dev/null

echo "=== Uploading new files ==="
mpremote cp src_code/config.py :config.py
mpremote cp src_code/motor.py :motor.py
mpremote cp src_code/sensor.py :sensor.py
mpremote cp src_code/controller.py :controller.py
mpremote cp src_code/calibration.py :calibration.py
mpremote cp src_code/fsm.py :fsm.py
mpremote cp src_code/main.py :main.py

echo "=== Resetting ESP32 ==="
mpremote reset

echo "=== Done! ==="
```

Chạy:
```bash
chmod +x upload.sh
./upload.sh
```

---

## ❓ Nếu vẫn lỗi

Chạy lệnh này để xem file config.py trên ESP32:
```bash
mpremote cat :config.py
```

Và gửi output cho tôi để kiểm tra.
