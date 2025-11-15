# Sửa lỗi "No module named 'requests'"

## Vấn đề
Khi chạy file EXE, gặp lỗi: `ModuleNotFoundError: No module named 'requests'`

## Nguyên nhân
PyInstaller không tự động phát hiện và bao gồm module `requests` và các dependencies của nó.

## Giải pháp

### Cách 1: Sử dụng file spec đã sửa
File `AutoClick.spec` đã được cập nhật để bao gồm:
- `requests` và tất cả dependencies (urllib3, certifi, charset_normalizer, idna)
- Sử dụng `collect_all('requests')` để đảm bảo tất cả files liên quan được include

Build lại:
```bash
pyinstaller AutoClick.spec --clean
```

### Cách 2: Sử dụng script build đã cập nhật
Chạy:
```bash
build_exe_simple.bat
```

Script đã được cập nhật với:
- `--collect-all=requests` để bao gồm tất cả dependencies
- `--hidden-import` cho các module cần thiết

## Kiểm tra

Sau khi build lại, chạy file EXE và kiểm tra:
1. Dialog kích hoạt key hiện ra
2. Có thể nhập key và kích hoạt
3. Ứng dụng chạy bình thường

## Lưu ý

Nếu vẫn gặp lỗi, thử:
1. Xóa thư mục `build` và `dist` cũ
2. Build lại với `--clean` flag
3. Kiểm tra tất cả dependencies đã được cài đặt: `pip install -r requirements.txt`

