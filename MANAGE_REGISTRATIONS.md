# Hướng dẫn Quản lý Đăng ký Máy

## 🎯 Tổng quan

Khi người dùng mở ứng dụng lần đầu, máy sẽ **tự động đăng ký lên GitHub** vào file `registrations.json`. Bạn chỉ cần vào GitHub để:
1. Xem danh sách máy đã đăng ký
2. Đặt thời gian hết hạn
3. Cấp quyền (approve) và tạo key

## 📋 File Registrations

File `registrations.json` trên GitHub có format:

```json
{
  "machines": [
    {
      "machine_id": "abc123...",
      "computer_name": "DESKTOP-ABC",
      "system": "Windows",
      "processor": "Intel64 Family 6",
      "platform": "Windows-10-10.0.22000",
      "registration_date": "2024-11-16T10:30:00",
      "status": "pending",
      "expire_date": null,
      "key_name": null
    }
  ]
}
```

## 🔧 Cách Quản lý

### Bước 1: Xem danh sách đăng ký

1. Truy cập: https://github.com/truongxoantit/autoclick
2. Mở file `registrations.json`
3. Xem danh sách các máy đã đăng ký

### Bước 2: Phê duyệt và tạo key

1. **Chọn máy cần phê duyệt** từ danh sách
2. **Tạo key mới** trong file `keys.json`:
   ```json
   {
     "key": "KEY-2024-001",
     "key_name": "Key cho máy ABC",
     "expire_date": "2025-12-31T23:59:59",
     "machine_id": "abc123...",
     "created_date": "2024-11-16T00:00:00"
   }
   ```
3. **Cập nhật status** trong `registrations.json`:
   - Đổi `"status": "pending"` → `"status": "approved"`
   - Đặt `"expire_date": "2025-12-31T23:59:59"`
   - Đặt `"key_name": "KEY-2024-001"`

### Bước 3: Từ chối (nếu cần)

Nếu không muốn cấp quyền:
```json
{
  "status": "rejected",
  "expire_date": null,
  "key_name": null
}
```

## 📝 Quy trình Hoàn chỉnh

1. **Người dùng mở ứng dụng lần đầu**
   - Ứng dụng tự động đăng ký máy lên GitHub
   - Machine ID được lưu vào `registrations.json`
   - Status: `pending`

2. **Admin xem đăng ký**
   - Vào GitHub xem file `registrations.json`
   - Xem thông tin máy: computer name, system, processor, registration date

3. **Admin tạo key và phê duyệt**
   - Tạo key mới trong `keys.json` với `machine_id` tương ứng
   - Cập nhật `registrations.json`: status = "approved", expire_date, key_name

4. **Người dùng sử dụng key**
   - Ứng dụng tự động kiểm tra key từ GitHub
   - Nếu key hợp lệ → ứng dụng hoạt động
   - Nếu key hết hạn → ứng dụng tự động đóng

## 🔑 Tạo Key

### Format Key trong keys.json:

```json
{
  "keys": [
    {
      "key": "KEY-2024-001",
      "key_name": "Key 1 tháng",
      "expire_date": "2025-01-31T23:59:59",
      "machine_id": "abc123def456...",
      "created_date": "2024-11-16T00:00:00"
    }
  ]
}
```

**Lưu ý**: `machine_id` phải khớp với `machine_id` trong `registrations.json`

## ⚙️ Tự động hóa (Tùy chọn)

Bạn có thể tạo script tự động để:
- Đọc `registrations.json`
- Tự động tạo key cho các máy `pending`
- Cập nhật status thành `approved`

## 📊 Trạng thái

- **pending**: Đang chờ phê duyệt
- **approved**: Đã được phê duyệt và có key
- **rejected**: Bị từ chối

## 🔒 Bảo mật

- File `registrations.json` là public (có thể xem)
- Machine ID là hash, không thể reverse về thông tin máy
- Chỉ admin mới có quyền edit file trên GitHub

## 💡 Tips

1. **Đặt tên key rõ ràng**: Ví dụ "Key 1 tháng - Máy ABC"
2. **Kiểm tra expire_date**: Đảm bảo format đúng ISO 8601
3. **Backup**: Nên backup file `keys.json` và `registrations.json` định kỳ
4. **Thông báo**: Có thể thông báo cho người dùng key đã được cấp qua email/chat

