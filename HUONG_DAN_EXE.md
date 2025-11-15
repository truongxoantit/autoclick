# Hướng dẫn Sử dụng File EXE

## 📦 File EXE

Sau khi build thành công, file EXE sẽ nằm tại: `dist/AutoClick.exe`

## 🚀 Cách Sử dụng

### Bước 1: Copy File EXE
- Copy file `AutoClick.exe` sang máy đích (máy cần sử dụng)
- Không cần cài đặt Python hay bất kỳ thư viện nào

### Bước 2: Chạy File EXE
- Double-click vào file `AutoClick.exe`
- Lần đầu chạy sẽ hiện dialog **Kích hoạt License Key**

### Bước 3: Kích hoạt Key
1. Nhập License Key vào ô nhập
2. Nhấn Enter hoặc click nút "✅ Kích hoạt"
3. Ứng dụng sẽ kiểm tra key với GitHub
4. Nếu key hợp lệ → Ứng dụng sẽ mở và sử dụng được

## 🔑 Dialog Kích hoạt Key

Dialog sẽ hiển thị:
- **Machine ID**: ID duy nhất của máy (mỗi máy chỉ dùng 1 key)
- **Ô nhập Key**: Nhập license key
- **Nút Kích hoạt**: Kích hoạt key
- **Nút Hủy**: Đóng ứng dụng nếu không có key

## ⚠️ Lưu ý

1. **Kết nối Internet**: Cần internet để kiểm tra key với GitHub lần đầu
2. **File license.key**: Sẽ được tạo tự động trong cùng thư mục với EXE
3. **Mỗi máy 1 key**: Một key chỉ dùng được trên 1 máy (theo Machine ID)
4. **Kiểm tra định kỳ**: Ứng dụng tự động kiểm tra key mỗi 5 phút
5. **Key hết hạn**: Ứng dụng sẽ tự động đóng nếu key hết hạn

## 🛠️ Quản lý Keys

Để thêm key mới hoặc quản lý keys, chỉnh sửa file `keys.json` trên GitHub:
- Repository: https://github.com/truongxoantit/autoclick
- File: `keys.json`

Format key:
```json
{
  "key": "YOUR-KEY-NAME",
  "key_name": "Key Name",
  "expire_date": "2025-12-31T23:59:59",
  "machine_id": null,
  "created_date": "2024-11-16T00:00:00"
}
```

## 📋 Tính năng

Sau khi kích hoạt key, ứng dụng có đầy đủ tính năng:
- ✅ Ghi lại thao tác (F4)
- ✅ Phát lại thao tác (F6)
- ✅ Tìm và click hình ảnh (F5)
- ✅ Script Editor với IF-ELSE (F8)
- ✅ Pick Image (F9)
- ✅ Get Position (F10)
- ✅ Undo/Redo (Ctrl+Z, Ctrl+Y)
- ✅ Pause/Resume (F11)
- ✅ Export/Import Actions
- ✅ Và nhiều tính năng khác...

## 🐛 Troubleshooting

### EXE không chạy được
- Kiểm tra Windows Defender/Antivirus (có thể block file)
- Thử chạy với quyền Administrator
- Kiểm tra file có bị corrupt không

### Key không kích hoạt được
- Kiểm tra kết nối internet
- Kiểm tra key có trong file `keys.json` trên GitHub
- Kiểm tra key chưa hết hạn
- Kiểm tra key chưa được dùng trên máy khác

### Ứng dụng tự động đóng
- Key đã hết hạn → Cần gia hạn key trên GitHub
- Key không hợp lệ → Kiểm tra lại key

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file `license.key` (nếu có)
2. Kiểm tra kết nối internet
3. Kiểm tra file `keys.json` trên GitHub

