"""
Script để build ứng dụng thành file EXE
"""
import PyInstaller.__main__
import os
import shutil

# Xóa thư mục build cũ nếu có
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('main.spec'):
    os.remove('main.spec')

# Các file cần include
datas = [
    ('SCRIPT_EXAMPLES.txt', '.'),
]

# Các module cần include
hiddenimports = [
    'pynput',
    'pynput.mouse',
    'pynput.keyboard',
    'PIL',
    'PIL.ImageGrab',
    'cv2',
    'numpy',
    'requests',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
]

# Build EXE
PyInstaller.__main__.run([
    'main.py',
    '--name=AutoClick',
    '--onefile',
    '--windowed',
    '--icon=NONE',  # Có thể thêm icon sau
    '--add-data=SCRIPT_EXAMPLES.txt;.',
    '--hidden-import=pynput',
    '--hidden-import=pynput.mouse',
    '--hidden-import=pynput.keyboard',
    '--hidden-import=PIL',
    '--hidden-import=PIL.ImageGrab',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--hidden-import=requests',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    '--hidden-import=tkinter.filedialog',
    '--hidden-import=tkinter.messagebox',
    '--hidden-import=tkinter.scrolledtext',
    '--collect-all=pynput',
    '--collect-all=PIL',
    '--collect-all=cv2',
    '--noconsole',  # Không hiện console window
])

print("\n" + "="*50)
print("Build thành công!")
print("File EXE tại: dist/AutoClick.exe")
print("="*50)

