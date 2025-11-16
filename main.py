"""
Ứng dụng Auto Click - Ghi lại và phát lại thao tác người dùng
Giao diện giống AutoMouse với bảng chỉnh sửa thao tác
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
from action_recorder import ActionRecorder
from action_player import ActionPlayer
from image_finder import ImageFinder
from script_executor import ScriptExecutor
from image_picker import ImagePicker
from region_selector import RegionSelector
from position_picker import PositionPicker
from key_manager import KeyManager
from key_activation_dialog import KeyActivationDialog
from pynput import keyboard
from pynput.mouse import Controller as MouseController
import time
import sys


class AutoClickApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Click - Automatic Mouse and Keyboard")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Khởi tạo các module
        self.recorder = ActionRecorder()
        self.player = ActionPlayer()
        self.image_finder = ImageFinder(confidence=0.8)
        self.script_executor = ScriptExecutor(image_finder=self.image_finder)
        self.image_picker = ImagePicker(save_directory="images")
        self.mouse_controller = MouseController()
        
        # Khởi tạo Key Manager
        self.key_manager = KeyManager(github_repo="truongxoantit/autoclick")
        
        # Kiểm tra key trước khi khởi động (chỉ hiện dialog nếu chưa có key)
        if not self.key_manager.check_key():
            # Hiển thị dialog kích hoạt key ngay khi khởi động
            dialog = KeyActivationDialog(self.root, self.key_manager)
            if not dialog.show():
                # Người dùng không kích hoạt key hoặc hủy
                messagebox.showerror("License Required", "Bạn cần kích hoạt key để sử dụng ứng dụng!")
                root.destroy()
                sys.exit(0)
        
        # Biến trạng thái
        self.recording_file = None
        self.playing_thread = None
        self.keyboard_listener = None
        self.actions_list = []  # Danh sách các hành động để hiển thị
        self.copied_action = None  # Hành động đã copy
        self.history = []  # Lịch sử để undo/redo
        self.history_index = -1
        self.is_paused = False  # Trạng thái pause
        
        # Tạo giao diện
        self.create_menu()
        self.create_toolbar()
        self.create_widgets()
        
        # Bắt đầu lắng nghe phím tắt
        self.setup_hotkeys()
        
    def create_menu(self):
        """Tạo menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo_action, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected, accelerator="Del")
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add Random Delay", command=self.add_random_delay)
        edit_menu.add_command(label="Bulk Edit Delay", command=self.bulk_edit_delay)
        
        # Insert menu
        insert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Insert", menu=insert_menu)
        insert_menu.add_command(label="Click", command=self.insert_click)
        insert_menu.add_command(label="Move", command=self.insert_move)
        insert_menu.add_command(label="Wait", command=self.insert_wait)
        insert_menu.add_command(label="Key", command=self.insert_key)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Find Image", command=self.show_find_image)
        tools_menu.add_command(label="Export Actions", command=self.export_actions)
        tools_menu.add_command(label="Import Actions", command=self.import_actions)
        tools_menu.add_separator()
        tools_menu.add_command(label="License Key", command=self.show_license_info)
        tools_menu.add_command(label="Activate Key", command=self.activate_license)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-z>', lambda e: self.undo_action())
        self.root.bind('<Control-y>', lambda e: self.redo_action())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<F11>', lambda e: self.pause_resume())
        
    def create_toolbar(self):
        """Tạo toolbar"""
        toolbar = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Record button
        self.record_btn = ttk.Button(toolbar, text="RECORD (F4)", command=self.toggle_recording, width=15)
        self.record_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Smart Click button
        ttk.Button(toolbar, text="SMART CLICK (F5)", command=self.smart_click, width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Pick Image button
        ttk.Button(toolbar, text="PICK IMAGE (F9)", command=self.pick_image, width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Get Position button
        ttk.Button(toolbar, text="GET POS (F10)", command=self.get_mouse_position, width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Play button
        self.play_btn = ttk.Button(toolbar, text="PLAY (F6)", command=self.toggle_playing, width=12)
        self.play_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Stop button
        self.stop_btn = ttk.Button(toolbar, text="STOP (F7)", command=self.stop_all, width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Pause/Resume button
        self.pause_btn = ttk.Button(toolbar, text="PAUSE (F11)", command=self.pause_resume, width=12, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Status label
        self.status_label = ttk.Label(toolbar, text="Ready", foreground="green")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # License status label
        self.license_label = ttk.Label(toolbar, text="", foreground="blue", font=("Arial", 8))
        self.license_label.pack(side=tk.RIGHT, padx=5)
        self.update_license_status()
        
        # Kiểm tra license định kỳ (mỗi 10 phút)
        self.check_license_periodically()
        
    def create_widgets(self):
        """Tạo các widget chính"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main frame với Notebook (Tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tab 1: Actions List
        actions_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(actions_tab, text="Actions")
        
        # Bảng hiển thị các thao tác (giống AutoMouse)
        actions_frame = ttk.LabelFrame(actions_tab, text="Actions", padding="5")
        actions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview với scrollbar
        tree_frame = ttk.Frame(actions_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo Treeview (nhỏ gọn hơn)
        columns = ('step', 'action', 'delay')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Định nghĩa columns (nhỏ gọn hơn)
        self.tree.heading('step', text='#')
        self.tree.heading('action', text='Action')
        self.tree.heading('delay', text='Delay(ms)')
        
        self.tree.column('step', width=50, anchor=tk.CENTER)
        self.tree.column('action', width=400, anchor=tk.W)
        self.tree.column('delay', width=80, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Bind double click để chỉnh sửa delay
        self.tree.bind('<Double-1>', self.edit_action)
        # Bind right click để menu context
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Toolbar cho actions
        actions_toolbar = ttk.Frame(actions_frame)
        actions_toolbar.pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_toolbar, text="Pick Image", command=self.pick_image, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Get Pos", command=self.get_mouse_position, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Screenshot", command=self.capture_screen, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Edit Delay", command=self.edit_selected_delay, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Bulk Delay", command=self.bulk_edit_delay, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Undo", command=self.undo_action, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(actions_toolbar, text="Redo", command=self.redo_action, width=8).pack(side=tk.LEFT, padx=1)
        
        # Play Options frame (nhỏ gọn hơn)
        play_options_frame = ttk.Frame(actions_tab)
        play_options_frame.pack(fill=tk.X, pady=2)
        
        # Repeat options (compact)
        self.repeat_var = tk.StringVar(value="once")
        ttk.Radiobutton(play_options_frame, text="Once", variable=self.repeat_var, value="once").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(play_options_frame, text="Repeat", variable=self.repeat_var, value="times").grid(row=0, column=1, padx=5)
        self.repeat_times_entry = ttk.Entry(play_options_frame, width=4)
        self.repeat_times_entry.insert(0, "10")
        self.repeat_times_entry.grid(row=0, column=2, padx=2)
        ttk.Label(play_options_frame, text="x").grid(row=0, column=3, padx=2)
        
        # Speed control (compact)
        ttk.Label(play_options_frame, text="Speed:").grid(row=0, column=4, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(play_options_frame, from_=0.1, to=5.0, variable=self.speed_var, orient=tk.HORIZONTAL, length=100)
        speed_scale.grid(row=0, column=5, padx=2)
        self.speed_label = ttk.Label(play_options_frame, text="1.0x", width=5)
        self.speed_label.grid(row=0, column=6, padx=2)
        speed_scale.configure(command=self.update_speed_label)
        
        # Checkboxes (compact)
        self.shutdown_var = tk.BooleanVar()
        ttk.Checkbutton(play_options_frame, text="Shutdown", variable=self.shutdown_var).grid(row=0, column=7, padx=5)
        
        self.no_activate_var = tk.BooleanVar()
        ttk.Checkbutton(play_options_frame, text="No activate", variable=self.no_activate_var).grid(row=0, column=8, padx=5)
        
        # Tab 2: Script Editor
        script_tab = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(script_tab, text="Script Editor")
        
        # Help text
        help_text = """# Script Editor với IF-ELSE (Giống AutoMouse)
# Cú pháp:
# if image "path.png" found
#     click x y delay
# else
#     click x y delay
# endif

# if window "Window Title" exists
#     click x y delay
# endif

# Ví dụ:
if image "button.png" found
    click 100 200 0.5
    wait 1.0
else
    click 300 400 0.5
endif

# Các lệnh:
click x y [delay]
rightclick x y [delay]
doubleclick x y [delay]
move x y [delay]
wait seconds
key "keyname" [delay]  # Ví dụ: "enter", "Ctrl+A"
type "text" [delay]
findimage "path.png" [x] [y] [width] [height]
scroll x y dx dy"""
        
        script_editor_frame = ttk.LabelFrame(script_tab, text="Script", padding="5")
        script_editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.script_text = scrolledtext.ScrolledText(script_editor_frame, height=25, wrap=tk.WORD, font=("Consolas", 10))
        self.script_text.pack(fill=tk.BOTH, expand=True)
        self.script_text.insert('1.0', help_text)
        
        # Script buttons
        script_btn_frame = ttk.Frame(script_tab)
        script_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(script_btn_frame, text="Run Script (F8)", command=self.run_script).pack(side=tk.LEFT, padx=5)
        ttk.Button(script_btn_frame, text="Load Script", command=self.load_script_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(script_btn_frame, text="Save Script", command=self.save_script_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(script_btn_frame, text="Stop", command=self.stop_script).pack(side=tk.LEFT, padx=5)
        
        self.loop_script_var = tk.BooleanVar()
        ttk.Checkbutton(script_btn_frame, text="Loop", variable=self.loop_script_var).pack(side=tk.LEFT, padx=10)
        
        self.script_status_label = ttk.Label(script_btn_frame, text="Ready", foreground="green")
        self.script_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Log area (nhỏ gọn hơn)
        self.log_frame = ttk.LabelFrame(actions_tab, text="Log", padding="3")
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=3, wrap=tk.WORD, font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_frame.pack(fill=tk.BOTH, expand=False, pady=2)
        
    def setup_hotkeys(self):
        """Thiết lập phím tắt"""
        def on_press(key):
            try:
                if key == keyboard.Key.f4:
                    self.root.after(0, self.toggle_recording)
                elif key == keyboard.Key.f5:
                    self.root.after(0, self.smart_click)
                elif key == keyboard.Key.f6:
                    self.root.after(0, self.toggle_playing)
                elif key == keyboard.Key.f7:
                    self.root.after(0, self.stop_all)
                elif key == keyboard.Key.f8:
                    self.root.after(0, self.run_script)
                elif key == keyboard.Key.f9:
                    self.root.after(0, self.pick_image)
                elif key == keyboard.Key.f10:
                    self.root.after(0, self.get_mouse_position)
            except:
                pass
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()
        
    def log(self, message: str):
        """Ghi log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def update_speed_label(self, value):
        """Cập nhật label tốc độ"""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
        self.player.speed_multiplier = speed
        
    def add_action_to_tree(self, step_num, action_desc, delay_ms):
        """Thêm hành động vào tree"""
        item = self.tree.insert('', tk.END, values=(step_num, action_desc, f"{delay_ms} ms"))
        return item
        
    def update_actions_display(self):
        """Cập nhật hiển thị các hành động"""
        # Xóa tất cả
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Thêm lại từ actions_list
        for idx, action in enumerate(self.actions_list, 1):
            step_num = str(idx)
            action_desc = action.get('description', 'Unknown action')
            delay_ms = action.get('delay', 0) * 1000  # Convert to ms
            self.add_action_to_tree(step_num, action_desc, delay_ms)
    
    # Menu functions
    def new_file(self):
        """Tạo file mới"""
        if messagebox.askyesno("Confirm", "Clear all actions?"):
            self.clear_all()
            self.log("Created new file")
    
    def open_file(self):
        """Mở file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            if filename.endswith('.json'):
                actions = self.recorder.load_from_file(filename)
                self.actions_list = [self._convert_action_to_dict(a) for a in actions]
            else:
                # Load script
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                actions = self.script_executor.parse_script(content)
                self.actions_list = [self._convert_script_action_to_dict(a) for a in actions]
            
            self.update_actions_display()
            self.log(f"Loaded {len(self.actions_list)} actions from {filename}")
    
    def save_file(self):
        """Lưu file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            if filename.endswith('.json'):
                # Save as JSON
                data = {
                    'created_at': datetime.now().isoformat(),
                    'total_actions': len(self.actions_list),
                    'actions': [self._dict_to_action(a) for a in self.actions_list]
                }
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                # Save as script
                script_lines = []
                for action in self.actions_list:
                    action_type = action.get('type')
                    if action_type == 'click':
                        x, y = action.get('x', 0), action.get('y', 0)
                        delay = action.get('delay', 0.1)
                        script_lines.append(f"click {x} {y} {delay}")
                    elif action_type == 'wait':
                        seconds = action.get('seconds', 1.0)
                        script_lines.append(f"wait {seconds}")
                    # Add more types as needed
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(script_lines))
            
            self.log(f"Saved {len(self.actions_list)} actions to {filename}")
    
    def delete_selected(self):
        """Xóa hành động được chọn"""
        selected = self.tree.selection()
        if selected:
            self._save_to_history()
            indices = sorted([self.tree.index(item) for item in selected], reverse=True)
            for idx in indices:
                if 0 <= idx < len(self.actions_list):
                    del self.actions_list[idx]
            self.update_actions_display()
            self.log("Deleted selected action(s)")
    
    def clear_all(self):
        """Xóa tất cả"""
        if messagebox.askyesno("Confirm", "Clear all actions?"):
            self._save_to_history()
            self.actions_list = []
            self.update_actions_display()
            self.log("Cleared all actions")
    
    def insert_click(self):
        """Chèn hành động click"""
        dialog = self._create_action_dialog("Click", ["X:", "Y:", "Delay (ms):"])
        if dialog:
            self._save_to_history()
            x, y, delay = dialog
            # Tính timestamp dựa trên actions hiện có
            last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
            new_time = last_time + (float(delay) / 1000)
            
            action = {
                'type': 'click',
                'x': int(x),
                'y': int(y),
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': float(delay) / 1000,
                'description': f'Mouse Left Click at ({x}, {y})'
            }
            self.actions_list.append(action)
            self.update_actions_display()
    
    def insert_move(self):
        """Chèn hành động move"""
        dialog = self._create_action_dialog("Move", ["X:", "Y:", "Delay (ms):"])
        if dialog:
            self._save_to_history()
            x, y, delay = dialog
            # Tính timestamp dựa trên actions hiện có
            last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
            new_time = last_time + (float(delay) / 1000)
            
            action = {
                'type': 'move',
                'x': int(x),
                'y': int(y),
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': float(delay) / 1000,
                'description': f'Move mouse to ({x}, {y})'
            }
            self.actions_list.append(action)
            self.update_actions_display()
    
    def insert_wait(self):
        """Chèn hành động wait"""
        dialog = self._create_action_dialog("Wait", ["Seconds:"])
        if dialog:
            self._save_to_history()
            seconds = float(dialog[0])
            
            # Tính timestamp
            last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
            new_time = last_time + seconds
            
            action = {
                'type': 'wait',
                'seconds': seconds,
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': seconds,
                'description': f'Delay {seconds} seconds'
            }
            self.actions_list.append(action)
            self.update_actions_display()
    
    def insert_key(self):
        """Chèn hành động key"""
        dialog = self._create_action_dialog("Key", ["Key name:", "Delay (ms):"])
        if dialog:
            self._save_to_history()
            key, delay = dialog
            
            # Tính timestamp
            last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
            new_time = last_time + (float(delay) / 1000)
            
            action = {
                'type': 'key',
                'key': key,
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': float(delay) / 1000,
                'description': f'Keystroke "{key}"'
            }
            self.actions_list.append(action)
            self.update_actions_display()
    
    def _create_action_dialog(self, title, fields):
        """Tạo dialog nhập liệu"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        entries = []
        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(dialog, width=20)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)
        
        result = [None]
        
        def ok():
            result[0] = [e.get() for e in entries]
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=ok).grid(row=len(fields), column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=len(fields), column=1, padx=10, pady=10)
        
        dialog.wait_window()
        return result[0]
    
    def edit_action(self, event):
        """Chỉnh sửa hành động khi double click"""
        item = self.tree.selection()[0]
        idx = self.tree.index(item)
        if 0 <= idx < len(self.actions_list):
            action = self.actions_list[idx]
            # Tạo dialog chỉnh sửa
            dialog = self._create_edit_dialog(action)
            if dialog:
                self.actions_list[idx] = dialog
                self.update_actions_display()
                self.log(f"Edited action {idx + 1}")
    
    def _create_edit_dialog(self, action):
        """Tạo dialog chỉnh sửa hành động"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Action")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = [None]
        
        ttk.Label(dialog, text="Action Type:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        type_label = ttk.Label(dialog, text=action.get('type', 'unknown'))
        type_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Delay editor
        ttk.Label(dialog, text="Delay (ms):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        delay_entry = ttk.Entry(dialog, width=20)
        delay_ms = action.get('delay', 0) * 1000
        delay_entry.insert(0, str(delay_ms))
        delay_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Description editor
        ttk.Label(dialog, text="Description:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        desc_text = scrolledtext.ScrolledText(dialog, height=5, width=30)
        desc_text.insert('1.0', action.get('description', ''))
        desc_text.grid(row=2, column=1, padx=10, pady=5)
        
        def ok():
            action['delay'] = float(delay_entry.get()) / 1000
            action['description'] = desc_text.get('1.0', tk.END).strip()
            result[0] = action
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(dialog, text="OK", command=ok).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=3, column=1, padx=10, pady=10)
        
        dialog.wait_window()
        return result[0]
    
    def toggle_recording(self):
        """Bật/tắt ghi lại (F4)"""
        if not self.recorder.is_recording:
            self.recorder.start_recording()
            self.record_btn.config(text="RECORDING (F4)", state=tk.DISABLED)
            self.status_label.config(text="Recording...", foreground="red")
            self.log("Started recording (F4)")
        else:
            self.recorder.stop_recording()
            # Chuyển đổi actions từ recorder sang format hiển thị
            self.actions_list = [self._convert_action_to_dict(a) for a in self.recorder.actions]
            self.update_actions_display()
            self.record_btn.config(text="RECORD (F4)", state=tk.NORMAL)
            self.status_label.config(text="Ready", foreground="green")
            self.log(f"Stopped recording. Captured {len(self.actions_list)} actions")
    
    def smart_click(self):
        """Smart click - tìm và tự động click hình ảnh (F5)"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.log(f"Smart click: Finding image {filename}")
            # Tự động click nếu tìm thấy
            success = self.image_finder.find_and_click(filename, delay=0.2)
            if success:
                position = self.image_finder.find_image(filename)
                # Tính timestamp
                last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
                new_time = last_time + 0.1
                
                action = {
                    'type': 'click',
                    'x': position[0],
                    'y': position[1],
                    'time': new_time,  # Timestamp để phát lại đúng tốc độ
                    'delay': 0.1,
                    'description': f'Smart Click at image ({position[0]}, {position[1]})'
                }
                self.actions_list.append(action)
                self.update_actions_display()
                self.log(f"Found and clicked at ({position[0]}, {position[1]})")
                messagebox.showinfo("Success", f"Image found and clicked at ({position[0]}, {position[1]})")
            else:
                messagebox.showwarning("Not Found", "Image not found on screen")
                self.log("Image not found")
    
    def toggle_playing(self):
        """Bật/tắt phát lại (F6)"""
        if self.player.is_playing:
            self.stop_all()
        else:
            if not self.actions_list:
                messagebox.showwarning("Warning", "No actions to play!")
                return
            
            # Chuyển đổi actions_list sang format cho player
            # Đảm bảo actions được sắp xếp theo timestamp
            actions = [self._dict_to_action(a) for a in self.actions_list]
            # Sắp xếp theo timestamp để đảm bảo thứ tự đúng
            actions.sort(key=lambda a: a.get('time', 0))
            
            # Tính toán repeat
            repeat_count = 1
            if self.repeat_var.get() == "times":
                try:
                    repeat_count = int(self.repeat_times_entry.get())
                except:
                    repeat_count = 1
            elif self.repeat_var.get() == "minutes":
                try:
                    minutes = int(self.repeat_minutes_entry.get())
                    # Ước tính số lần lặp (giả sử mỗi lần chạy mất ~10 giây)
                    repeat_count = minutes * 6  # 6 lần mỗi phút
                except:
                    repeat_count = 1
            
            # Phát lại trong thread
            self.playing_thread = threading.Thread(
                target=self._play_actions_thread,
                args=(actions, repeat_count),
                daemon=True
            )
            self.playing_thread.start()
            
            self.play_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Playing...", foreground="blue")
            self.log(f"Started playing {len(actions)} actions (repeat {repeat_count} times)")
    
    def _play_actions_thread(self, actions, repeat_count):
        """Thread phát lại thao tác với hỗ trợ pause"""
        try:
            self.player.is_playing = True
            for i in range(repeat_count):
                if not self.player.is_playing:
                    break
                self.root.after(0, lambda i=i: self.log(f"Playing repeat {i + 1}/{repeat_count}"))
                
                # Chờ nếu đang pause
                while self.is_paused and self.player.is_playing:
                    time.sleep(0.1)
                
                self.player.play_actions(actions, loop=False)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error playing: {e}"))
        finally:
            self.player.is_playing = False
            self.is_paused = False
            self.root.after(0, self._on_play_finished)
    
    def _on_play_finished(self):
        """Callback khi phát lại xong"""
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED, text="PAUSE (F11)")
        self.is_paused = False
        self.status_label.config(text="Ready", foreground="green")
        self.log("Finished playing")
        
        if self.shutdown_var.get():
            self.log("Shutting down...")
            os.system("shutdown /s /t 0")
    
    def stop_all(self):
        """Dừng tất cả (F7)"""
        self.player.stop()
        self.script_executor.stop()
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="orange")
        self.log("Stopped all actions")
    
    def run_script(self):
        """Chạy script từ editor (F8)"""
        script_content = self.script_text.get('1.0', tk.END).strip()
        if not script_content:
            messagebox.showwarning("Warning", "Script is empty!")
            return
        
        try:
            actions = self.script_executor.parse_script(script_content)
            self.log(f"Parsed {len(actions)} actions from script")
            
            # Chạy trong thread
            self.script_thread = threading.Thread(
                target=self._run_script_thread,
                args=(actions,),
                daemon=True
            )
            self.script_thread.start()
            
            self.script_status_label.config(text="Running...", foreground="blue")
            self.status_label.config(text="Running Script...", foreground="blue")
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing script:\n{e}")
            self.log(f"Script error: {e}")
    
    def _run_script_thread(self, actions):
        """Thread chạy script"""
        try:
            def callback(msg):
                self.root.after(0, lambda: self.log(msg))
            
            self.script_executor.execute_actions(actions, loop=self.loop_script_var.get(), callback=callback)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Script execution error: {e}"))
        finally:
            self.root.after(0, self._on_script_finished)
    
    def _on_script_finished(self):
        """Callback khi script chạy xong"""
        self.script_status_label.config(text="Finished", foreground="green")
        self.status_label.config(text="Ready", foreground="green")
        self.log("Script finished")
    
    def stop_script(self):
        """Dừng script"""
        self.script_executor.stop()
        self.script_status_label.config(text="Stopped", foreground="red")
        self.log("Script stopped")
    
    def load_script_file(self):
        """Tải script từ file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.script_text.delete('1.0', tk.END)
            self.script_text.insert('1.0', content)
            self.log(f"Loaded script from {filename}")
    
    def save_script_file(self):
        """Lưu script ra file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            content = self.script_text.get('1.0', tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"Saved script to {filename}")
    
    def show_find_image(self):
        """Hiển thị dialog tìm hình ảnh"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            position = self.image_finder.find_image(filename)
            if position:
                messagebox.showinfo("Found", f"Image found at ({position[0]}, {position[1]})")
            else:
                messagebox.showwarning("Not Found", "Image not found on screen")
    
    def show_settings(self):
        """Hiển thị settings"""
        messagebox.showinfo("Settings", "Settings dialog - Coming soon!")
    
    def pick_image(self):
        """Chụp và lưu ảnh từ màn hình (F9)"""
        self.root.withdraw()  # Ẩn cửa sổ chính
        time.sleep(0.3)  # Chờ một chút
        
        try:
            selector = RegionSelector(self.root)
            region = selector.select_region()
            
            if region:
                x1, y1, x2, y2 = region
                filepath = self.image_picker.capture_region(x1, y1, x2, y2)
                self.log(f"Image saved: {filepath}")
                messagebox.showinfo("Success", f"Image saved to:\n{filepath}")
                
                # Hỏi có muốn thêm vào actions không
                if messagebox.askyesno("Add Action", "Add 'Find Image' action to list?"):
                    # Tính timestamp
                    last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
                    new_time = last_time + 0.5
                    
                    action = {
                        'type': 'findimage',
                        'image_path': filepath,
                        'time': new_time,  # Timestamp để phát lại đúng tốc độ
                        'delay': 0.5,
                        'description': f'Find Image: {os.path.basename(filepath)}'
                    }
                    self.actions_list.append(action)
                    self.update_actions_display()
        except Exception as e:
            self.log(f"Error picking image: {e}")
        finally:
            self.root.deiconify()  # Hiện lại cửa sổ chính
    
    def get_mouse_position(self):
        """Lấy vị trí chuột bằng cách pick với Ctrl (F10)"""
        def on_pick(x, y):
            # Copy vào clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(f"{x}, {y}")
            
            # Tính timestamp
            last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
            new_time = last_time + 0.1
            
            action = {
                'type': 'click',
                'x': x,
                'y': y,
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': 0.1,
                'description': f'Mouse Click at ({x}, {y})'
            }
            self.actions_list.append(action)
            self.update_actions_display()
            self.log(f"Picked position: ({x}, {y}) - Copied to clipboard")
        
        position_picker = PositionPicker(self.root)
        position_picker.pick_position(callback=on_pick)
    
    def capture_screen(self):
        """Chụp toàn màn hình"""
        filepath = self.image_picker.capture_full_screen()
        self.log(f"Screenshot saved: {filepath}")
        messagebox.showinfo("Success", f"Screenshot saved to:\n{filepath}")
    
    def edit_selected_delay(self):
        """Chỉnh sửa delay của hành động được chọn"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an action first!")
            return
        
        item = selected[0]
        idx = self.tree.index(item)
        if 0 <= idx < len(self.actions_list):
            self.edit_action(None)
    
    def show_context_menu(self, event):
        """Hiển thị menu context khi right click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit Delay", command=self.edit_selected_delay)
            menu.add_command(label="Delete", command=self.delete_selected)
            menu.add_separator()
            menu.add_command(label="Copy", command=self.copy_action)
            menu.add_command(label="Paste", command=self.paste_action)
            
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
    
    def copy_action(self):
        """Copy hành động được chọn"""
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            if 0 <= idx < len(self.actions_list):
                self.copied_action = self.actions_list[idx].copy()
                self.log("Action copied")
    
    def paste_action(self):
        """Paste hành động đã copy"""
        if hasattr(self, 'copied_action') and self.copied_action:
            self._save_to_history()
            self.actions_list.append(self.copied_action.copy())
            self.update_actions_display()
            self.log("Action pasted")
        else:
            messagebox.showwarning("Warning", "No action copied!")
    
    def _save_to_history(self):
        """Lưu trạng thái vào history để undo"""
        self.history = self.history[:self.history_index + 1]
        self.history.append([a.copy() for a in self.actions_list])
        self.history_index = len(self.history) - 1
        if len(self.history) > 50:  # Giới hạn 50 lần undo
            self.history.pop(0)
            self.history_index -= 1
    
    def undo_action(self):
        """Undo hành động cuối"""
        if self.history_index > 0:
            self.history_index -= 1
            self.actions_list = [a.copy() for a in self.history[self.history_index]]
            self.update_actions_display()
            self.log("Undo")
        else:
            messagebox.showinfo("Info", "Nothing to undo")
    
    def redo_action(self):
        """Redo hành động"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.actions_list = [a.copy() for a in self.history[self.history_index]]
            self.update_actions_display()
            self.log("Redo")
        else:
            messagebox.showinfo("Info", "Nothing to redo")
    
    def bulk_edit_delay(self):
        """Chỉnh delay hàng loạt cho tất cả actions hoặc actions được chọn"""
        if not self.actions_list:
            messagebox.showwarning("Warning", "No actions to edit!")
            return
        
        # Lấy các items được chọn
        selected_items = self.tree.selection()
        selected_indices = []
        
        if selected_items:
            # Chỉ chỉnh delay cho các items được chọn
            for item in selected_items:
                try:
                    index = int(self.tree.item(item, 'values')[0]) - 1
                    if 0 <= index < len(self.actions_list):
                        selected_indices.append(index)
                except:
                    pass
        else:
            # Chỉnh delay cho tất cả actions
            selected_indices = list(range(len(self.actions_list)))
        
        if not selected_indices:
            messagebox.showwarning("Warning", "No actions selected!")
            return
        
        # Tạo dialog để nhập delay
        dialog = tk.Toplevel(self.root)
        dialog.title("Bulk Edit Delay")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {'apply': False, 'mode': 'set', 'value': 0.1, 'multiplier': 1.0}
        
        # Info
        info_label = ttk.Label(
            dialog,
            text=f"Editing delay for {len(selected_indices)} action(s)",
            font=("Arial", 10, "bold")
        )
        info_label.pack(pady=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(dialog, text="Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=20, pady=10)
        
        mode_var = tk.StringVar(value="set")
        
        def update_mode():
            result['mode'] = mode_var.get()
            if mode_var.get() == "set":
                value_entry.config(state=tk.NORMAL)
                multiplier_entry.config(state=tk.DISABLED)
            else:
                value_entry.config(state=tk.NORMAL if mode_var.get() == "add" else tk.DISABLED)
                multiplier_entry.config(state=tk.NORMAL if mode_var.get() == "multiply" else tk.DISABLED)
        
        ttk.Radiobutton(
            mode_frame,
            text="Set fixed delay (seconds)",
            variable=mode_var,
            value="set",
            command=update_mode
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            mode_frame,
            text="Multiply current delay by",
            variable=mode_var,
            value="multiply",
            command=update_mode
        ).pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Radiobutton(
            mode_frame,
            text="Add to current delay (seconds)",
            variable=mode_var,
            value="add",
            command=update_mode
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Value input
        value_frame = ttk.Frame(dialog, padding="10")
        value_frame.pack(fill=tk.X, padx=20)
        
        ttk.Label(value_frame, text="Delay value:").pack(side=tk.LEFT, padx=5)
        value_entry = ttk.Entry(value_frame, width=15)
        value_entry.insert(0, "0.1")
        value_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(value_frame, text="seconds").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(value_frame, text="Multiplier:").pack(side=tk.LEFT, padx=5)
        multiplier_entry = ttk.Entry(value_frame, width=15)
        multiplier_entry.insert(0, "1.0")
        multiplier_entry.config(state=tk.DISABLED)
        multiplier_entry.pack(side=tk.LEFT, padx=5)
        
        # Preview
        preview_label = ttk.Label(
            dialog,
            text="",
            font=("Arial", 9),
            foreground="blue"
        )
        preview_label.pack(pady=5)
        
        def update_preview():
            try:
                if mode_var.get() == "set":
                    val = float(value_entry.get())
                    preview_label.config(text=f"All delays will be set to {val} seconds")
                elif mode_var.get() == "multiply":
                    mult = float(multiplier_entry.get())
                    preview_label.config(text=f"All delays will be multiplied by {mult}")
                else:  # add
                    val = float(value_entry.get())
                    preview_label.config(text=f"{val} seconds will be added to all delays")
            except:
                preview_label.config(text="Invalid input")
        
        value_entry.bind('<KeyRelease>', lambda e: update_preview())
        multiplier_entry.bind('<KeyRelease>', lambda e: update_preview())
        update_preview()
        
        # Buttons
        btn_frame = ttk.Frame(dialog, padding="20")
        btn_frame.pack(fill=tk.X)
        
        def apply():
            try:
                result['mode'] = mode_var.get()
                if mode_var.get() == "set":
                    result['value'] = float(value_entry.get())
                elif mode_var.get() == "multiply":
                    result['multiplier'] = float(multiplier_entry.get())
                else:  # add
                    result['value'] = float(value_entry.get())
                
                result['apply'] = True
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Please enter a valid number.")
        
        ttk.Button(btn_frame, text="Apply", command=apply, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        
        if result['apply']:
            # Lưu vào history
            self._save_to_history()
            
            # Áp dụng delay
            modified_count = 0
            for idx in selected_indices:
                action = self.actions_list[idx]
                current_delay = action.get('delay', 0.1)
                
                if result['mode'] == "set":
                    new_delay = result['value']
                elif result['mode'] == "multiply":
                    new_delay = current_delay * result['multiplier']
                else:  # add
                    new_delay = current_delay + result['value']
                
                # Đảm bảo delay không âm
                new_delay = max(0.0, new_delay)
                action['delay'] = new_delay
                modified_count += 1
            
            self.update_actions_display()
            self.log(f"Bulk edited delay for {modified_count} action(s)")
            messagebox.showinfo("Success", f"Updated delay for {modified_count} action(s)!")
    
    def add_random_delay(self):
        """Thêm delay ngẫu nhiên vào các hành động"""
        import random
        self._save_to_history()
        for action in self.actions_list:
            if 'delay' in action:
                # Thêm random delay từ 0.1 đến 0.5 giây
                random_delay = random.uniform(0.1, 0.5)
                action['delay'] = action.get('delay', 0.1) + random_delay
        self.update_actions_display()
        self.log("Added random delays to all actions")
    
    def pause_resume(self):
        """Pause/Resume phát lại (F11)"""
        if self.player.is_playing:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_btn.config(text="RESUME (F11)")
                self.status_label.config(text="Paused", foreground="orange")
                self.log("Paused")
            else:
                self.pause_btn.config(text="PAUSE (F11)")
                self.status_label.config(text="Playing...", foreground="blue")
                self.log("Resumed")
    
    def export_actions(self):
        """Export actions ra file CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Step', 'Action', 'Delay (ms)'])
                for idx, action in enumerate(self.actions_list, 1):
                    delay_ms = action.get('delay', 0) * 1000
                    writer.writerow([idx, action.get('description', ''), f"{delay_ms:.1f}"])
            self.log(f"Exported {len(self.actions_list)} actions to {filename}")
            messagebox.showinfo("Success", f"Exported to {filename}")
    
    def import_actions(self):
        """Import actions từ file CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                import csv
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    imported = 0
                    for row in reader:
                        if len(row) >= 2:
                            # Parse từ CSV (cần cải thiện parser)
                            imported += 1
                self.log(f"Imported {imported} actions from {filename}")
                messagebox.showinfo("Success", f"Imported from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error importing: {e}")
                self.log(f"Import error: {e}")
    
    def _convert_action_to_dict(self, action):
        """Chuyển đổi action từ recorder format sang dict - GIỮ LẠI TIMESTAMP"""
        action_type = action.get('type', '')
        x = action.get('x', 0)
        y = action.get('y', 0)
        time_val = action.get('time', 0)  # Timestamp gốc từ recorder
        
        # Tính delay dựa trên timestamp (sẽ được tính khi phát lại)
        # Nhưng cũng lưu delay mặc định để hiển thị
        if action_type == 'click' or 'press_left' in action_type:
            return {
                'type': 'click',
                'x': x,
                'y': y,
                'time': time_val,  # GIỮ LẠI timestamp gốc
                'delay': 0.1,  # Delay mặc định để hiển thị
                'description': f'Mouse Left Click at ({x}, {y})'
            }
        elif action_type == 'move':
            return {
                'type': 'move',
                'x': x,
                'y': y,
                'time': time_val,  # GIỮ LẠI timestamp gốc
                'delay': 0.1,  # Delay mặc định để hiển thị
                'description': f'Move mouse to ({x}, {y})'
            }
        elif action_type == 'press_right' or 'right' in action_type:
            return {
                'type': 'rightclick',
                'x': x,
                'y': y,
                'time': time_val,  # GIỮ LẠI timestamp gốc
                'delay': 0.1,
                'description': f'Mouse Right Click at ({x}, {y})'
            }
        elif action_type == 'scroll':
            return {
                'type': 'scroll',
                'x': x,
                'y': y,
                'dx': action.get('dx', 0),
                'dy': action.get('dy', 0),
                'time': time_val,  # GIỮ LẠI timestamp gốc
                'delay': 0.1,
                'description': f'Scroll at ({x}, {y})'
            }
        elif action_type == 'wait':
            return {
                'type': 'wait',
                'seconds': time_val,
                'time': time_val,  # GIỮ LẠI timestamp gốc
                'delay': time_val,
                'description': f'Delay {time_val} seconds'
            }
        else:
            return {
                'type': action_type,
                'x': x,
                'y': y,
                'delay': 0.1,
                'description': f'{action_type} at ({x}, {y})'
            }
    
    def _convert_script_action_to_dict(self, action):
        """Chuyển đổi script action sang dict - tính timestamp"""
        action_type = action.get('type', '')
        
        # Tính timestamp dựa trên actions hiện có
        last_time = self.actions_list[-1].get('time', 0) if self.actions_list else 0
        delay = action.get('delay', 0.1)
        new_time = last_time + delay
        
        if action_type == 'click':
            return {
                'type': 'click',
                'x': action.get('x', 0),
                'y': action.get('y', 0),
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': delay,
                'description': f'Mouse Left Click at ({action.get("x", 0)}, {action.get("y", 0)})'
            }
        elif action_type == 'wait':
            seconds = action.get('seconds', 1.0)
            return {
                'type': 'wait',
                'seconds': seconds,
                'time': new_time,  # Timestamp để phát lại đúng tốc độ
                'delay': seconds,
                'description': f'Delay {seconds} seconds'
            }
        else:
            # Thêm time nếu chưa có
            if 'time' not in action:
                action['time'] = new_time
            return action
    
    def _dict_to_action(self, action_dict):
        """Chuyển đổi dict sang action format cho player - GIỮ LẠI TIMESTAMP"""
        action_type = action_dict.get('type', '')
        time_val = action_dict.get('time', 0)  # Lấy timestamp gốc
        
        if action_type == 'click':
            return {
                'type': 'press_left',
                'x': action_dict.get('x', 0),
                'y': action_dict.get('y', 0),
                'time': time_val  # GIỮ LẠI timestamp để tính delay chính xác
            }
        elif action_type == 'move':
            return {
                'type': 'move',
                'x': action_dict.get('x', 0),
                'y': action_dict.get('y', 0),
                'time': time_val  # GIỮ LẠI timestamp để tính delay chính xác
            }
        elif action_type == 'rightclick':
            return {
                'type': 'press_right',
                'x': action_dict.get('x', 0),
                'y': action_dict.get('y', 0),
                'time': time_val
            }
        elif action_type == 'scroll':
            return {
                'type': 'scroll',
                'x': action_dict.get('x', 0),
                'y': action_dict.get('y', 0),
                'dx': action_dict.get('dx', 0),
                'dy': action_dict.get('dy', 0),
                'time': time_val
            }
        elif action_type == 'wait':
            return {
                'type': 'wait',
                'seconds': action_dict.get('seconds', 1.0),
                'time': time_val  # Sử dụng timestamp gốc
            }
        else:
            # Giữ nguyên nếu đã có time
            if 'time' not in action_dict:
                action_dict['time'] = 0
            return action_dict
    
    def check_license(self) -> bool:
        """Kiểm tra license key"""
        if not self.key_manager.check_key():
            # Hiển thị dialog kích hoạt key
            dialog = KeyActivationDialog(self.root, self.key_manager)
            if dialog.show():
                return True
            else:
                messagebox.showerror("License Required", "Bạn cần kích hoạt key để sử dụng ứng dụng!")
                return False
        return True
    
    def show_license_info(self):
        """Hiển thị thông tin license"""
        key_info = self.key_manager.get_key_info()
        if key_info:
            info_text = f"Key Name: {key_info['key_name']}\n"
            info_text += f"Expire Date: {key_info['expire_date']}\n"
            info_text += f"Days Remaining: {key_info['days_remaining']} days\n"
            info_text += f"Machine ID: {self.key_manager.get_machine_id()}"
            messagebox.showinfo("License Information", info_text)
        else:
            messagebox.showwarning("No License", "Chưa có key được kích hoạt!")
    
    def activate_license(self):
        """Kích hoạt license key mới"""
        dialog = KeyActivationDialog(self.root, self.key_manager)
        if dialog.show():
            self.update_license_status()
            messagebox.showinfo("Success", "Key đã được kích hoạt thành công!")
    
    def update_license_status(self):
        """Cập nhật trạng thái license trên toolbar"""
        key_info = self.key_manager.get_key_info()
        if key_info:
            days = key_info['days_remaining']
            if days > 30:
                color = "green"
            elif days > 7:
                color = "orange"
            else:
                color = "red"
            self.license_label.config(
                text=f"License: {key_info['key_name']} ({days}d)",
                foreground=color
            )
        else:
            self.license_label.config(text="No License", foreground="red")
    
    def check_license_periodically(self):
        """Kiểm tra license định kỳ - mỗi 10 phút"""
        if not self.key_manager.check_key():
            messagebox.showerror(
                "License Expired",
                "Key của bạn đã hết hạn! Ứng dụng sẽ đóng sau 5 giây."
            )
            self.root.after(5000, lambda: sys.exit(0))
        else:
            self.update_license_status()
            # Kiểm tra lại sau 10 phút (600000ms)
            self.root.after(600000, self.check_license_periodically)


def main():
    root = tk.Tk()
    app = AutoClickApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
