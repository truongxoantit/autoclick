# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Collect all data files
datas = [('SCRIPT_EXAMPLES.txt', '.')]
binaries = []

# Hidden imports - tất cả các module cần thiết
hiddenimports = [
    # Core modules
    'pynput', 'pynput.mouse', 'pynput.keyboard', 'pynput.mouse._win32', 'pynput.keyboard._win32',
    'PIL', 'PIL.Image', 'PIL.ImageGrab', 'PIL.ImageTk',
    'cv2', 'cv2.cv2',
    'numpy', 'numpy.core', 'numpy.core._multiarray_umath',
    'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
    'pygetwindow',
    'keyboard',
    # Tkinter và submodules
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext',
    'tkinter.font', 'tkinter.constants',
    # Custom modules
    'action_recorder', 'action_player', 'image_finder', 'script_executor',
    'image_picker', 'region_selector', 'key_manager', 'key_activation_dialog',
    'auto_registration',
    # Standard library modules (đảm bảo)
    'threading', 'json', 'hashlib', 'platform', 'datetime', 'time', 'sys', 'os', 'typing', 're',
]

# Collect all dependencies với collect_all
print("Collecting pynput...")
tmp_ret = collect_all('pynput')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

print("Collecting PIL...")
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

print("Collecting cv2...")
tmp_ret = collect_all('cv2')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

print("Collecting numpy...")
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

print("Collecting requests...")
tmp_ret = collect_all('requests')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Collect submodules cho các packages lớn
print("Collecting submodules...")
hiddenimports += collect_submodules('pynput')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('cv2')

# Loại bỏ duplicates
hiddenimports = list(set(hiddenimports))
datas = list(set(datas))
binaries = list(set(binaries))

print(f"Total hidden imports: {len(hiddenimports)}")
print(f"Total data files: {len(datas)}")
print(f"Total binaries: {len(binaries)}")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Loại trừ các module không cần thiết để giảm kích thước
        'matplotlib', 'scipy', 'pandas', 'jupyter', 'IPython',
        'test', 'tests', 'unittest', 'pydoc', 'doctest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoClick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Nén để giảm kích thước
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Không hiện console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
