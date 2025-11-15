# Auto Click - Automatic Mouse and Keyboard

Ứng dụng tự động hóa thao tác chuột và bàn phím giống AutoMouse, không sử dụng Windows API, hoàn toàn mô phỏng như người dùng thật.

## ✨ Tính năng

### 🎯 Cơ bản
- **Ghi lại thao tác**: Ghi lại tất cả click, di chuyển chuột, cuộn (F4)
- **Phát lại thao tác**: Phát lại với tốc độ tùy chỉnh, lặp lại (F6)
- **Tìm và click hình ảnh**: Tự động tìm và click vào hình ảnh trên màn hình (F5)
- **Pick Image**: Chụp vùng màn hình và lưu tự động (F9)
- **Get Position**: Lấy vị trí chuột hiện tại (F10)

### 🚀 Nâng cao
- **Script Editor với IF-ELSE**: Viết script tự động với điều kiện if-else (F8)
- **Undo/Redo**: Hoàn tác và làm lại các thao tác (Ctrl+Z, Ctrl+Y)
- **Pause/Resume**: Tạm dừng và tiếp tục phát lại (F11)
- **Random Delay**: Thêm delay ngẫu nhiên để tự nhiên hơn
- **Export/Import**: Xuất/nhập actions ra CSV
- **Copy/Paste Actions**: Sao chép và dán hành động
- **Chỉnh sửa Delay**: Double-click để chỉnh delay cho từng hành động

### 🎨 Giao diện
- Bảng chỉnh sửa thao tác giống AutoMouse
- Tab Actions và Script Editor
- Toolbar với các phím tắt
- Log area để theo dõi hoạt động

## 📋 Yêu cầu

- Python 3.7+
- Windows 10/11
- Các thư viện trong `requirements.txt`

## 🔧 Cài đặt

### Cách 1: Sử dụng pip (Khuyến nghị)
```bash
pip install -r requirements.txt
```

### Cách 2: Sử dụng mirror (Nếu có vấn đề kết nối)
```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

Hoặc chạy file batch:
```bash
install_with_mirror.bat
```

## 🚀 Sử dụng

### Chạy ứng dụng:
```bash
python main.py
```

### Phím tắt:
- **F4**: Bật/tắt ghi lại thao tác
- **F5**: Smart Click - Tìm và tự động click hình ảnh
- **F6**: Phát lại thao tác
- **F7**: Dừng tất cả
- **F8**: Chạy script
- **F9**: Pick Image - Chụp vùng màn hình
- **F10**: Get Position - Lấy vị trí chuột
- **F11**: Pause/Resume phát lại
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+S**: Lưu file
- **Del**: Xóa hành động được chọn

### Ghi lại thao tác:
1. Nhấn **F4** hoặc nút "RECORD"
2. Thực hiện các thao tác chuột/bàn phím
3. Nhấn **F4** lại để dừng
4. Các thao tác sẽ tự động hiển thị trong bảng

### Tìm và click hình ảnh:
1. Nhấn **F5** hoặc nút "SMART CLICK"
2. Chọn file hình ảnh cần tìm
3. Ứng dụng sẽ **tự động tìm và click** vào hình ảnh nếu tìm thấy

### Pick Image:
1. Nhấn **F9** hoặc nút "PICK IMAGE"
2. Kéo chuột để chọn vùng màn hình
3. Ảnh sẽ tự động lưu vào thư mục `images/`
4. Có thể thêm hành động "Find Image" vào danh sách

### Script Editor với IF-ELSE:
```python
# Ví dụ script
if image "button.png" found
    click 100 200 0.5
    wait 1.0
else
    click 300 400 0.5
endif

if window "Notepad" exists
    click 50 50 0.3
    type "Hello" 0.05
    key "enter" 0.2
endif
```

## 📁 Cấu trúc Project

```
autoclick/
├── main.py                 # Giao diện chính
├── action_recorder.py      # Module ghi lại thao tác
├── action_player.py        # Module phát lại thao tác
├── image_finder.py         # Module tìm kiếm hình ảnh
├── image_picker.py         # Module chụp và lưu ảnh
├── region_selector.py      # Module chọn vùng màn hình
├── script_executor.py      # Module thực thi script với if-else
├── requirements.txt        # Danh sách thư viện
├── README.md              # Hướng dẫn này
├── SCRIPT_EXAMPLES.txt    # Ví dụ script
├── install_with_mirror.bat # Script cài đặt với mirror
└── images/                # Thư mục lưu ảnh (tự động tạo)
```

## 🎯 Tính năng đặc biệt

### Không sử dụng Windows API
- Sử dụng `pynput` để mô phỏng thao tác chuột ở mức thấp
- Chụp màn hình bằng `PIL.ImageGrab` thay vì Windows API
- Hoàn toàn giống người dùng thật, không bị phát hiện

### Script với IF-ELSE
- Hỗ trợ điều kiện: `if image found`, `if window exists`
- Có thể lồng nhiều điều kiện
- Cú pháp giống AutoMouse

### Tự động click khi tìm thấy ảnh
- Smart Click (F5) **tự động click** vào hình ảnh nếu tìm thấy
- Không cần thao tác thủ công

## 📝 Ví dụ Script

Xem file `SCRIPT_EXAMPLES.txt` để biết thêm ví dụ.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📄 License

MIT License

## ⚠️ Lưu ý

- Ứng dụng này chỉ dùng cho mục đích hợp pháp
- Người dùng chịu trách nhiệm về cách sử dụng
- Có thể cần quyền quản trị cho một số thao tác

## 🐛 Báo lỗi

Nếu gặp lỗi, vui lòng tạo issue trên GitHub với:
- Mô tả lỗi
- Các bước để tái hiện
- Log từ ứng dụng (nếu có)
