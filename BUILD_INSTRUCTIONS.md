# Hướng dẫn Build File EXE

## Yêu cầu

- Python 3.7+
- Tất cả các thư viện trong `requirements.txt` đã được cài đặt

## Cách 1: Sử dụng Script Tự động (Khuyến nghị)

### Windows:
```bash
build_exe.bat
```

Script sẽ:
1. Tự động kiểm tra và cài đặt PyInstaller nếu chưa có
2. Build file EXE
3. File EXE sẽ nằm trong thư mục `dist/AutoClick.exe`

## Cách 2: Build Thủ công

### Bước 1: Cài đặt PyInstaller
```bash
pip install pyinstaller
```

### Bước 2: Build EXE
```bash
pyinstaller --name=AutoClick --onefile --windowed --noconsole main.py
```

Hoặc sử dụng file spec:
```bash
pyinstaller AutoClick.spec
```

## Cấu trúc File EXE

File EXE sẽ bao gồm:
- Tất cả các module Python cần thiết
- Thư viện đã được đóng gói
- File `SCRIPT_EXAMPLES.txt`
- Không cần cài đặt Python trên máy đích

## Sử dụng File EXE

1. Copy file `dist/AutoClick.exe` sang máy đích
2. Chạy file EXE
3. Lần đầu chạy sẽ hiện dialog nhập key
4. Nhập key và kích hoạt
5. Ứng dụng sẽ tự động kiểm tra key với GitHub

## Lưu ý

- File EXE có thể lớn (~50-100MB) do bao gồm tất cả thư viện
- Lần đầu chạy có thể hơi chậm (Windows Defender scan)
- Cần kết nối internet để kiểm tra key với GitHub
- File `license.key` sẽ được tạo trong cùng thư mục với EXE

## Troubleshooting

### Lỗi: "Failed to execute script"
- Kiểm tra xem tất cả dependencies đã được cài đặt chưa
- Thử build lại với `--debug=all` để xem lỗi chi tiết

### EXE không chạy được
- Kiểm tra Windows Defender/Antivirus (có thể block file)
- Thử chạy với quyền Administrator
- Kiểm tra log file nếu có

### Key không kích hoạt được
- Kiểm tra kết nối internet
- Kiểm tra file `keys.json` trên GitHub có đúng format không
- Kiểm tra key có trong danh sách và chưa hết hạn

## Tùy chỉnh

### Thêm Icon:
1. Tạo file `icon.ico`
2. Sửa `AutoClick.spec`: `icon='icon.ico'`
3. Build lại

### Thay đổi tên file:
Sửa `--name=AutoClick` thành tên mong muốn

