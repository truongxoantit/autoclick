# Hệ thống Quản lý License Key

## Tổng quan

Ứng dụng Auto Click sử dụng hệ thống quản lý license key tích hợp với GitHub để:
- Kiểm tra key theo thời gian thực
- Quản lý thời gian hết hạn
- Đảm bảo mỗi máy chỉ sử dụng 1 key
- Tự động đóng ứng dụng khi key hết hạn

## Cấu trúc

### File `keys.json` trên GitHub

File này chứa danh sách tất cả các key hợp lệ, được lưu tại:
`https://raw.githubusercontent.com/truongxoantit/autoclick/main/keys.json`

Format:
```json
{
  "keys": [
    {
      "key": "DEMO-KEY-2024-001",
      "key_name": "Demo Key 1",
      "expire_date": "2025-12-31T23:59:59",
      "machine_id": null,
      "created_date": "2024-01-01T00:00:00"
    }
  ]
}
```

### File `license.key` (Local)

File này lưu thông tin key đã kích hoạt trên máy, bao gồm:
- Key value
- Machine ID
- Key name
- Expire date
- Registered date

## Cách hoạt động

1. **Khi khởi động ứng dụng:**
   - Kiểm tra file `license.key` local
   - Kiểm tra key với GitHub
   - Nếu không có key hoặc key hết hạn → Hiển thị dialog kích hoạt

2. **Khi kích hoạt key:**
   - Người dùng nhập key
   - Ứng dụng kiểm tra key với GitHub
   - Kiểm tra thời gian hết hạn
   - Kiểm tra machine_id (mỗi máy chỉ dùng 1 key)
   - Lưu key vào file local

3. **Kiểm tra định kỳ:**
   - Mỗi 5 phút kiểm tra lại key
   - Nếu key hết hạn → Thông báo và đóng ứng dụng sau 5 giây

## Quản lý Keys trên GitHub

### Thêm key mới:

1. Mở file `keys.json` trên GitHub
2. Thêm key mới vào mảng `keys`:
```json
{
  "key": "NEW-KEY-2024-001",
  "key_name": "New Key Name",
  "expire_date": "2025-12-31T23:59:59",
  "machine_id": null,
  "created_date": "2024-11-16T00:00:00"
}
```

### Xóa key:

Xóa object key khỏi mảng `keys` trong file `keys.json`

### Gia hạn key:

Cập nhật `expire_date` trong file `keys.json`

## Machine ID

Mỗi máy có một Machine ID duy nhất được tạo từ:
- Computer name
- Operating system
- Processor information

Machine ID được hash bằng MD5 để đảm bảo tính duy nhất.

## Tính năng

- ✅ Kiểm tra key theo thời gian thực từ GitHub
- ✅ Quản lý thời gian hết hạn
- ✅ Mỗi máy chỉ dùng 1 key (kiểm tra machine_id)
- ✅ Tự động đóng khi key hết hạn
- ✅ Hiển thị thông tin license trên toolbar
- ✅ Menu quản lý license (Tools → License Key / Activate Key)

## Lưu ý

1. File `keys.json` phải được commit và push lên GitHub để ứng dụng có thể kiểm tra
2. File `license.key` được ignore bởi Git (không commit lên GitHub)
3. Nếu không có internet, ứng dụng vẫn hoạt động với key đã lưu local (nhưng không kiểm tra được với GitHub)

