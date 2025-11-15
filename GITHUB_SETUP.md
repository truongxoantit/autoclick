# Hướng dẫn đưa lên GitHub

## Bước 1: Khởi tạo Git repository

```bash
git init
```

## Bước 2: Thêm các file

```bash
git add .
```

## Bước 3: Commit

```bash
git commit -m "Initial commit: Auto Click application with image recognition and if-else scripting"
```

## Bước 4: Tạo repository trên GitHub

1. Đăng nhập GitHub
2. Tạo repository mới (ví dụ: `autoclick`)
3. Không tích "Initialize with README" (vì đã có README.md)

## Bước 5: Kết nối và push

```bash
git remote add origin https://github.com/YOUR_USERNAME/autoclick.git
git branch -M main
git push -u origin main
```

## Cấu trúc file sẽ được đưa lên:

- ✅ `main.py` - Giao diện chính
- ✅ `action_recorder.py` - Module ghi lại
- ✅ `action_player.py` - Module phát lại
- ✅ `image_finder.py` - Module tìm ảnh
- ✅ `image_picker.py` - Module chụp ảnh
- ✅ `region_selector.py` - Module chọn vùng
- ✅ `script_executor.py` - Module thực thi script
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Hướng dẫn
- ✅ `SCRIPT_EXAMPLES.txt` - Ví dụ script
- ✅ `.gitignore` - Ignore files
- ✅ `install_with_mirror.bat` - Script cài đặt

## Files sẽ bị ignore (theo .gitignore):

- `__pycache__/`
- `images/*.png`, `images/*.jpg` (ảnh đã chụp)
- `*.json` (file actions đã lưu)
- `*.log`

