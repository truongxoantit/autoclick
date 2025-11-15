@echo off
chcp 65001 >nul
echo ========================================
echo BUILD EXE - AUTO CLICK
echo ========================================
echo.

echo Đang build file EXE...
echo (Quá trình này có thể mất vài phút...)
echo.

pyinstaller --name=AutoClick --onefile --windowed --noconsole ^
    --add-data="SCRIPT_EXAMPLES.txt;." ^
    --hidden-import=pynput ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=PIL ^
    --hidden-import=PIL.ImageGrab ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=charset_normalizer ^
    --hidden-import=idna ^
    --collect-all=pynput ^
    --collect-all=PIL ^
    --collect-all=cv2 ^
    --collect-all=requests ^
    main.py

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

