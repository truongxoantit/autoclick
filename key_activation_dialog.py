"""
Dialog kích hoạt key license
"""
import tkinter as tk
from tkinter import ttk, messagebox
from key_manager import KeyManager
import time


class KeyActivationDialog:
    def __init__(self, parent, key_manager: KeyManager):
        self.parent = parent
        self.key_manager = key_manager
        self.result = False
        
        # Tạo dialog nhỏ gọn
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("License Key")
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Focus vào entry
        self.key_entry.focus_set()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.activate_key())
    
    def create_widgets(self):
        """Tạo các widget - nhỏ gọn, chỉ có ô nhập key"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(
            main_frame,
            text="Nhập License Key:",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Key input
        self.key_entry = ttk.Entry(main_frame, width=40, font=("Consolas", 11))
        self.key_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Kích hoạt",
            command=self.activate_key,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="Hủy",
            command=self.cancel,
            width=15
        ).pack(side=tk.LEFT)
        
        # Status (ẩn cho đến khi có lỗi)
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=("Arial", 8),
            foreground="red"
        )
        self.status_label.pack(pady=(5, 0))
    
    def activate_key(self):
        """Kích hoạt key"""
        key = self.key_entry.get().strip()
        
        if not key:
            self.status_label.config(text="❌ Vui lòng nhập key!", foreground="red")
            self.key_entry.focus_set()
            return
        
        # Disable button khi đang kiểm tra
        for widget in self.dialog.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state=tk.DISABLED)
        
        self.status_label.config(text="⏳ Đang kiểm tra key với GitHub...", foreground="blue")
        self.dialog.update()
        
        # Đăng ký key
        if self.key_manager.register_key(key):
            self.status_label.config(text="✅ Key đã được kích hoạt thành công!", foreground="green")
            self.dialog.update()
            time.sleep(1)  # Hiển thị thông báo thành công 1 giây
            self.result = True
            self.dialog.destroy()
        else:
            # Enable lại button
            for widget in self.dialog.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.config(state=tk.NORMAL)
            self.status_label.config(text="❌ Key không hợp lệ, đã hết hạn hoặc đã được sử dụng trên máy khác!", foreground="red")
            self.key_entry.focus_set()
            self.key_entry.select_range(0, tk.END)
    
    def cancel(self):
        """Hủy"""
        self.dialog.destroy()
    
    def show(self):
        """Hiển thị dialog và chờ kết quả"""
        self.dialog.wait_window()
        return self.result

