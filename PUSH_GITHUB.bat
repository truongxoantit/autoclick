@echo off
chcp 65001 >nul
echo ========================================
echo PUSH TO GITHUB - AUTOCLICK
echo ========================================
echo.

echo Bước 1: Tạo repository trên GitHub
echo.
echo Vui lòng làm theo các bước sau:
echo 1. Mở trình duyệt và truy cập: https://github.com/new
echo 2. Repository name: autoclick
echo 3. Description: Auto Click - Automatic Mouse and Keyboard
echo 4. Chọn Public hoặc Private
echo 5. KHÔNG tích "Initialize with README"
echo 6. Click "Create repository"
echo.
pause

echo.
echo Bước 2: Nhập thông tin GitHub
echo.
set /p GITHUB_USER="Nhập GitHub username của bạn: "

echo.
echo Đang thêm remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/truongxoantit/autoclick.git

echo.
echo Đang push lên GitHub...
echo (Có thể cần nhập username và password/token)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo THÀNH CÔNG!
    echo ========================================
    echo.
    echo Repository của bạn tại:
    echo https://github.com/truongxoantit/autoclick
    echo.
) else (
    echo.
    echo ========================================
    echo CÓ LỖI XẢY RA
    echo ========================================
    echo.
    echo Nếu lỗi authentication:
    echo 1. Tạo Personal Access Token tại:
    echo    https://github.com/settings/tokens
    echo 2. Chọn quyền: repo
    echo 3. Dùng token làm password khi push
    echo.
)

pause

