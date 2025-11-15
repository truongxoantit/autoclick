@echo off
chcp 65001 >nul
echo ========================================
echo BUILD EXE OPTIMIZED - AUTO CLICK
echo ========================================
echo.

echo Đang build file EXE với tối ưu đầy đủ...
echo (Quá trình này có thể mất 5-10 phút...)
echo.

REM Xóa build cũ
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Sử dụng file spec đã tối ưu...
pyinstaller AutoClick.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo THÀNH CÔNG!
    echo ========================================
    echo.
    echo File EXE tại: dist\AutoClick.exe
    echo.
    echo File EXE này có thể chạy trên bất kỳ máy Windows nào
    echo mà KHÔNG CẦN cài đặt Python hay bất kỳ thư viện nào!
    echo.
    echo Tất cả dependencies đã được đóng gói vào file EXE.
    echo.
) else (
    echo.
    echo ========================================
    echo CÓ LỖI XẢY RA
    echo ========================================
    echo.
    echo Kiểm tra lại:
    echo 1. Tất cả dependencies đã được cài đặt: pip install -r requirements.txt
    echo 2. PyInstaller đã được cài đặt: pip install pyinstaller
    echo.
)

pause

