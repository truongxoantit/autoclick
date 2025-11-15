"""
Dialog kích hoạt key license
"""
import tkinter as tk
from tkinter import ttk, messagebox
from key_manager import KeyManager


class KeyActivationDialog:
    def __init__(self, parent, key_manager: KeyManager):
        self.parent = parent
        self.key_manager = key_manager
        self.result = False
        
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Kích hoạt License Key")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
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
        """Tạo các widget"""
        # Header
        header_frame = ttk.Frame(self.dialog, padding="20")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame,
            text="Kích hoạt License Key",
            font=("Arial", 16, "bold")
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Nhập key để sử dụng ứng dụng",
            font=("Arial", 10)
        ).pack(pady=(5, 0))
        
        # Machine ID
        info_frame = ttk.LabelFrame(self.dialog, text="Thông tin máy", padding="10")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        machine_id = self.key_manager.get_machine_id()
        ttk.Label(info_frame, text=f"Machine ID: {machine_id}", font=("Consolas", 9)).pack(anchor=tk.W)
        ttk.Label(
            info_frame,
            text="Mỗi máy chỉ có thể sử dụng 1 key",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Key input
        key_frame = ttk.LabelFrame(self.dialog, text="License Key", padding="10")
        key_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(key_frame, text="Nhập key:").pack(anchor=tk.W)
        self.key_entry = ttk.Entry(key_frame, width=50, font=("Consolas", 11))
        self.key_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog, padding="20")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Kích hoạt",
            command=self.activate_key,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Hủy",
            command=self.cancel,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(
            self.dialog,
            text="",
            font=("Arial", 9),
            foreground="red"
        )
        self.status_label.pack(pady=10)
    
    def activate_key(self):
        """Kích hoạt key"""
        key = self.key_entry.get().strip()
        
        if not key:
            self.status_label.config(text="Vui lòng nhập key!", foreground="red")
            return
        
        self.status_label.config(text="Đang kiểm tra key...", foreground="blue")
        self.dialog.update()
        
        # Đăng ký key
        if self.key_manager.register_key(key):
            self.result = True
            self.dialog.destroy()
        else:
            self.status_label.config(text="Key không hợp lệ hoặc đã hết hạn!", foreground="red")
    
    def cancel(self):
        """Hủy"""
        self.dialog.destroy()
    
    def show(self):
        """Hiển thị dialog và chờ kết quả"""
        self.dialog.wait_window()
        return self.result

