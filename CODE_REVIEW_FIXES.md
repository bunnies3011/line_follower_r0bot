# Code Review & Fixes - FSM và Config

**Ngày:** 2026-06-03  
**Phạm vi:** Kiểm tra thuật toán trong `fsm.py` và cấu hình trong `config.py`

---

## ✅ Các Vấn Đề Đã Fix

### 1. **Logic góc vuông bị chậm 1 vòng lặp** ⚠️ **CRITICAL**

**Vấn đề:**
- Khi phát hiện góc vuông trong `_follow_line()` (lines 260-276), code chỉ gọi `_change_state()` mà không thực thi lệnh turn ngay
- Xe phải đợi vòng lặp tiếp theo (STATE_TURN_LEFT_1/RIGHT_1) mới thực sự quay
- Độ trễ ~3ms (LOOP_DELAY_MS) khiến xe mất cơ hội quay kịp ở góc vuông gắt

**Giải pháp:**
```python
# TRƯỚC (fsm.py lines 260-266)
if (self._bitmask & MASK_SHARP_LEFT) == MASK_SHARP_LEFT:
    self.remember_line = -1
    self._change_state(STATE_TURN_LEFT_1)  # Chỉ đổi state
    return

# SAU (đã fix)
if (self._bitmask & MASK_SHARP_LEFT) == MASK_SHARP_LEFT:
    self.remember_line = -1
    self._last_search_direction = -1
    self._remember_ms = time.ticks_ms()
    self._turn_left_hard()  # ✅ Thực thi turn ngay lập tức
    self._change_state(STATE_TURN_LEFT_1)
    return
```

**Impact:** Giảm response time xuống còn 0ms, cải thiện đáng kể khả năng bám góc vuông.

---

### 2. **MASK_CENTER quá hẹp** ⚠️ **HIGH PRIORITY**

**Vấn đề:**
- `MASK_CENTER = 0x18` (00011000) chỉ kiểm tra sensor 4+5
- Khi line hơi lệch, xe không thoát được STATE_TURN_LEFT_1/RIGHT_1
- Xe quay quá đà hoặc bị kẹt trong state turn

**Giải pháp:**
```python
# TRƯỚC (config.py line 90)
MASK_CENTER = 0x18  # 00011000 → chỉ 2 sensor giữa

# SAU (đã fix)
MASK_CENTER = 0x3C  # 00111100 → 4 sensor giữa (sensor 2,3,4,5)
```

**Bit mapping:**
```
Bit:  7    6    5    4    3    2    1    0
      S8   S7   S6   S5   S4   S3   S2   S1
Old:  0    0    0    1    1    0    0    0  (0x18)
New:  0    0    1    1    1    1    0    0  (0x3C)
```

**Impact:** Dễ dàng detect "line về giữa", thoát state turn nhanh hơn, giảm overshoot.

---

### 3. **REMEMBER_TIMEOUT quá ngắn** ⚠️ **MEDIUM**

**Vấn đề:**
- `REMEMBER_TIMEOUT = 350ms` - quá ngắn với xe chạy nhanh
- Nếu có đoạn thẳng dài giữa 2 cua, hướng nhớ bị xóa trước khi đến cua
- Xe mất khả năng dự đoán hướng rẽ

**Giải pháp:**
```python
# TRƯỚC (config.py line 63)
REMEMBER_TIMEOUT = 350  # ms

# SAU (đã fix)
REMEMBER_TIMEOUT = 500  # ms – tăng 43% để đủ thời gian qua đoạn thẳng
```

**Tính toán:**
- Với tốc độ ~155/255 * 100% ≈ 60% max speed
- Quãng đường trong 500ms đủ để giữ remember qua đoạn thẳng ~30cm
- Vẫn đủ ngắn để tránh nhớ sai hướng sau khi đã ổn định

**Impact:** Cải thiện khả năng dự đoán hướng rẽ khi mất line.

---

### 4. **STATE_SEARCH_LINE thiếu fallback** ⚠️ **MEDIUM**

**Vấn đề:**
- Khi timeout, code chạy thẳng với `self.speed` (full speed)
- Nếu thực sự mất line (line đứt, xe ra ngoài track), chạy nhanh sẽ càng xa line
- Không có cơ chế giảm tốc để recovery

**Giải pháp:**
```python
# TRƯỚC (fsm.py lines 298-311)
if elapsed >= SEARCH_TURN_TIMEOUT_MS:
    self._drive_straight(self.speed)  # Full speed - nguy hiểm
    self._change_state(STATE_FOLLOW)
    return

# SAU (đã fix)
if elapsed >= SEARCH_TURN_TIMEOUT_MS:
    self._drive_straight(self.speed // 2)  # ✅ Giảm 50% tốc độ
    self._change_state(STATE_FOLLOW)
    return
```

**Logic:**
- Khi timeout → chạy chậm lại (50% speed) để tăng cơ hội sensor bắt lại line
- Thêm docstring giải thích chiến lược tránh dao động

**Impact:** Tăng recovery rate khi mất line hoàn toàn, giảm risk bay ra track.

---

## 📊 Tổng Hợp Thay Đổi

### File: `src_code/fsm.py`
- **Lines 260-277:** Thêm `_turn_left_hard()` / `_turn_right_hard()` ngay khi phát hiện góc vuông
- **Lines 300-318:** Cải thiện `_search_line()` với fallback giảm tốc

### File: `src_code/config.py`
- **Line 90:** MASK_CENTER: `0x18` → `0x3C` (mở rộng từ 2 sang 4 sensor)
- **Line 63:** REMEMBER_TIMEOUT: `350ms` → `500ms` (tăng 43%)

---

## ⚠️ Lưu Ý Pylance Warnings

Các warning về `time.ticks_ms()` là **BÌnh thường** vì:
- Đây là hàm của **MicroPython**, không phải Python tiêu chuẩn
- Pylance (type checker) không nhận diện MicroPython modules
- Code sẽ chạy bình thường trên ESP32 với MicroPython firmware

**Không cần fix** - bỏ qua warnings này.

---

## 🧪 Khuyến Nghị Test

### Test 1: Góc vuông gắt
- Track với góc 90° liên tục
- **Expected:** Xe quay nhanh, không bị trượt ra ngoài
- **Metric:** Response time < 10ms

### Test 2: Đoạn thẳng dài
- Track có đoạn thẳng 30-50cm giữa 2 cua
- **Expected:** Xe vẫn nhớ hướng cua trước khi đến cua tiếp theo
- **Metric:** remember_line != 0 sau đoạn thẳng

### Test 3: Recovery sau mất line
- Cố tình đẩy xe ra ngoài line
- **Expected:** Xe chạy chậm lại, quét tìm line, recovery thành công
- **Metric:** Recovery trong vòng 1-2 giây

### Test 4: Transition giữa các state
- Quan sát chuyển state từ FOLLOW → TURN_LEFT_1 → FOLLOW
- **Expected:** Chuyển mượt mà, không bị kẹt trong state TURN
- **Metric:** Thời gian ở state TURN < 500ms

---

## 🔧 Tùy Chỉnh Thêm (Tùy Chọn)

Nếu sau khi test vẫn gặp vấn đề, có thể điều chỉnh:

### Option A: MASK_CENTER còn chặt
Nếu xe vẫn không thoát state turn:
```python
MASK_CENTER = 0x7E  # 01111110 → 6 sensor giữa (loại trừ 2 sensor ngoài cùng)
```

### Option B: ADAPTIVE_SPEED_CURVE_THRESHOLD cần tune
Nếu xe giảm tốc quá sớm hoặc quá muộn:
```python
ADAPTIVE_SPEED_CURVE_THRESHOLD = 30  # Giảm xuống 30 để giảm tốc sớm hơn
# hoặc
ADAPTIVE_SPEED_CURVE_THRESHOLD = 40  # Tăng lên 40 để giữ tốc độ cao hơn
```

### Option C: SEARCH_TURN_TIMEOUT_MS cần điều chỉnh
Nếu xe quét quá nhanh hoặc quá chậm:
```python
SEARCH_TURN_TIMEOUT_MS = 300  # Giảm để thoát nhanh hơn
# hoặc
SEARCH_TURN_TIMEOUT_MS = 450  # Tăng để quét lâu hơn
```

---

## ✅ Kết Luận

Các vấn đề chính đã được fix:
1. ✅ Response time góc vuông: 0ms (đã loại bỏ độ trễ 1 vòng lặp)
2. ✅ Exit condition từ state turn: mở rộng từ 2 sang 4 sensor
3. ✅ Remember duration: tăng 43% để bao phủ đoạn thẳng dài
4. ✅ Recovery safety: giảm tốc 50% khi timeout search

**Tổng impact:** Cải thiện đáng kể khả năng bám đường, đặc biệt ở góc vuông và recovery sau mất line.

**Next step:** Upload code lên ESP32 và test thực tế trên track.

---

# UPDATE: Fix Vấn Đề Cua Tròn Bị Khựng

**Ngày cập nhật:** 2026-06-03 (buổi chiều)  
**Vấn đề mới:** Xe chạy tốt ở góc vuông nhưng bị "khựng" search lâu ở cua tròn

## 🔍 Nguyên Nhân

**MASK_SHARP_LEFT_MIN (0xE0) và MASK_SHARP_RIGHT_MIN (0x07) quá nhạy:**

```
Cua tròn tự nhiên: 00011000 → 00111000 → 01110000 → 11100000
                                                      ^^^^^^^^ Trigger tank turn!
```

- Pattern **11100000** (3 sensor) ở cua tròn bị hiểu nhầm là góc vuông
- Xe chuyển sang tank turn không cần thiết
- Khựng trong STATE_TURN_LEFT_1 chờ line về giữa (500ms timeout)
- Mất momentum và không mượt

## ✅ Giải Pháp Đã Implement

### **1. Bỏ MIN Masks Khỏi Logic Sharp Turn**

**File: `fsm.py` lines 258-278**

```python
# TRƯỚC: Trigger với 3 hoặc 4 sensor
if (self._bitmask & MASK_SHARP_LEFT) == MASK_SHARP_LEFT or \
   (self._bitmask & MASK_SHARP_LEFT_MIN) == MASK_SHARP_LEFT_MIN:  # ❌
   
# SAU: Chỉ trigger với 4 sensor
if (self._bitmask & MASK_SHARP_LEFT) == MASK_SHARP_LEFT:  # ✅
```

### **2. Giảm TURN_TIMEOUT_MS**

**File: `config.py` line 64**

```python
# TRƯỚC
TURN_TIMEOUT_MS = 500  # ms

# SAU
TURN_TIMEOUT_MS = 400  # ms – Cân bằng cho góc vuông thật + thoát nhanh nếu false positive
```

**Lý do 400ms:**
- Đủ cho motor với quán tính + ramping quay góc vuông
- Không quá lâu nếu có false positive
- Sensor smoothing (alpha=0.35) cần thời gian phản ứng

### **3. Đánh Dấu MIN Masks Deprecated**

**File: `config.py` lines 97-101**

```python
# DEPRECATED: MIN masks quá nhạy, trigger false positive ở cua tròn
# Chỉ dùng masks 4 sensor để tránh tank turn không cần thiết
MASK_SHARP_LEFT_MIN = 0xE0  # 11100000 → KHÔNG DÙNG (gây khựng ở cua tròn)
MASK_SHARP_RIGHT_MIN = 0x07 # 00000111 → KHÔNG DÙNG (gây khựng ở cua tròn)
```

## 📊 Pattern Handling Sau Fix

| Bitmask | Pattern | Hành Động | Status |
|---------|---------|-----------|--------|
| `0xFF` | 11111111 | Ngã tư → STATE_INTERSECTION | ✅ |
| `0xF0` | 11110000 | **Góc vuông TRÁI** → Tank turn | ✅ |
| `0x0F` | 00001111 | **Góc vuông PHẢI** → Tank turn | ✅ |
| `0xE0` | 11100000 | **Cua tròn gắt** → PD control | ✅ FIXED |
| `0x07` | 00000111 | **Cua tròn gắt** → PD control | ✅ FIXED |
| `0x70` | 01110000 | Cua tròn vừa → PD control | ✅ |
| `0x3C` | 00111100 | Line giữa → PD control | ✅ |
| `0x00` | 00000000 | Mất line → Search/straight | ✅ |

## 🎯 Kết Quả Mong Đợi

**TRƯỚC:**
- ❌ Góc vuông: Tank turn → OK
- ❌ Cua tròn: Tank turn sai → Khựng 500ms → Mất momentum

**SAU:**
- ✅ Góc vuông: Tank turn (4 sensor) → OK
- ✅ Cua tròn: PD control (3 sensor) → Mượt mà
- ✅ Timeout nhanh hơn: 400ms thay vì 500ms

## 📝 Summary All Changes

### Code Changes:
1. ✅ `fsm.py` line 260, 269: Bỏ `MASK_SHARP_LEFT_MIN` và `MASK_SHARP_RIGHT_MIN`
2. ✅ `config.py` line 64: `TURN_TIMEOUT_MS = 500` → `400`
3. ✅ `config.py` line 97-101: Đánh dấu MIN masks deprecated

### Impact:
- 🎯 **Cua tròn**: Không bị khựng, PD control mượt mà
- 🎯 **Góc vuông**: Vẫn tank turn chính xác (chỉ 4 sensor)
- 🎯 **Performance**: Giảm 100ms timeout, thoát nhanh hơn

**Test recommendation:** Chạy track có cả góc vuông 90° và cua tròn để verify cả 2 case.
