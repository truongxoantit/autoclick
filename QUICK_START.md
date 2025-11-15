# Quick Start - Đưa lên GitHub

## Cách 1: Sử dụng script tự động

1. Chạy file: `push_to_github.bat`
2. Làm theo hướng dẫn trong script

## Cách 2: Làm thủ công

### Bước 1: Tạo repository trên GitHub

1. Truy cập: https://github.com/new
2. Repository name: `autoclick`
3. Description: `Auto Click - Automatic Mouse and Keyboard with image recognition`
4. Chọn Public hoặc Private
5. **KHÔNG** tích "Initialize with README"
6. Click "Create repository"

### Bước 2: Chạy các lệnh sau

```bash
# Nếu chưa khởi tạo git
git init
git add .
git commit -m "Initial commit: Auto Click application"

# Thêm remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/autoclick.git
git branch -M main
git push -u origin main
```

### Bước 3: Xác thực

Nếu được hỏi username/password:
- Username: Tên GitHub của bạn
- Password: Sử dụng Personal Access Token (không phải password thường)

Tạo Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Chọn quyền: `repo`
4. Copy token và dùng làm password

## Sau khi push thành công

Repository sẽ có tại:
`https://github.com/YOUR_USERNAME/autoclick`

