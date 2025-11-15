@echo off
echo ========================================
echo CAI DAT CAC THU VIEN BANG MIRROR
echo ========================================
echo.

echo Dang cai dat pynput...
pip install -i https://mirrors.aliyun.com/pypi/simple/ pynput
if %errorlevel% neq 0 (
    echo Thu mirror khac...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ pynput
)

echo Dang cai dat pyautogui...
pip install -i https://mirrors.aliyun.com/pypi/simple/ pyautogui
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ pyautogui
)

echo Dang cai dat opencv-python...
pip install -i https://mirrors.aliyun.com/pypi/simple/ opencv-python
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ opencv-python
)

echo Dang cai dat numpy...
pip install -i https://mirrors.aliyun.com/pypi/simple/ numpy
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ numpy
)

echo Dang cai dat Pillow...
pip install -i https://mirrors.aliyun.com/pypi/simple/ Pillow
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ Pillow
)

echo Dang cai dat keyboard...
pip install -i https://mirrors.aliyun.com/pypi/simple/ keyboard
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ keyboard
)

echo Dang cai dat pygetwindow...
pip install -i https://mirrors.aliyun.com/pypi/simple/ pygetwindow
if %errorlevel% neq 0 (
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ pygetwindow
)

echo.
echo ========================================
echo HOAN TAT!
echo ========================================
pause

