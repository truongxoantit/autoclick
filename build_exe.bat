@echo off
chcp 65001 >nul
echo ========================================
echo BUILD EXE - AUTO CLICK
echo ========================================
echo.

echo Bước 1: Kiểm tra PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller chưa được cài đặt!
    echo Đang cài đặt PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Lỗi cài đặt PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo Bước 2: Đang build EXE...
echo (Quá trình này có thể mất vài phút...)
echo.

python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo THÀNH CÔNG!
    echo ========================================
    echo.
    echo File EXE tại: dist\AutoClick.exe
    echo.
    echo Bạn có thể copy file này sang máy khác để sử dụng!
    echo.
) else (
    echo.
    echo ========================================
    echo CÓ LỖI XẢY RA
    echo ========================================
    echo.
)

pause

