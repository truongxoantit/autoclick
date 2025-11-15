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
        
        # Tạo dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Kích hoạt License Key - Auto Click")
        self.dialog.geometry("550x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Đảm bảo dialog luôn ở trên cùng
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
        """Tạo các widget"""
        # Header
        header_frame = ttk.Frame(self.dialog, padding="20")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame,
            text="🔑 Kích hoạt License Key",
            font=("Arial", 18, "bold")
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Nhập key để sử dụng ứng dụng Auto Click",
            font=("Arial", 10),
            foreground="gray"
        ).pack(pady=(5, 0))
        
        # Thông tin thêm
        info_text = ttk.Label(
            header_frame,
            text="Key sẽ được kiểm tra với GitHub để xác thực",
            font=("Arial", 8),
            foreground="blue"
        )
        info_text.pack(pady=(5, 0))
        
        # Machine ID
        info_frame = ttk.LabelFrame(self.dialog, text="Thông tin máy", padding="10")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        machine_id = self.key_manager.get_machine_id()
        ttk.Label(info_frame, text=f"Machine ID: {machine_id}", font=("Consolas", 9)).pack(anchor=tk.W)
        
        # Kiểm tra trạng thái đăng ký
        if hasattr(self.key_manager, 'auto_registration'):
            reg_status = self.key_manager.auto_registration.get_registration_status()
            if reg_status:
                status_text = f"Trạng thái: {reg_status.get('status', 'pending')}"
                if reg_status.get('status') == 'approved':
                    status_color = "green"
                elif reg_status.get('status') == 'rejected':
                    status_color = "red"
                else:
                    status_color = "orange"
                ttk.Label(
                    info_frame,
                    text=status_text,
                    font=("Arial", 8),
                    foreground=status_color
                ).pack(anchor=tk.W, pady=(2, 0))
        
        ttk.Label(
            info_frame,
            text="Máy đã được tự động đăng ký lên GitHub. Vui lòng chờ admin phê duyệt.",
            font=("Arial", 8),
            foreground="blue"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Key input
        key_frame = ttk.LabelFrame(self.dialog, text="License Key", padding="10")
        key_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(key_frame, text="Nhập License Key:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.key_entry = ttk.Entry(key_frame, width=50, font=("Consolas", 12))
        self.key_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Hướng dẫn
        help_label = ttk.Label(
            key_frame,
            text="💡 Nhập key bạn đã nhận được và nhấn Enter hoặc nút 'Kích hoạt'",
            font=("Arial", 8),
            foreground="gray"
        )
        help_label.pack(anchor=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog, padding="20")
        btn_frame.pack(fill=tk.X)
        
        # Button frame với center alignment
        btn_center = ttk.Frame(btn_frame)
        btn_center.pack()
        
        activate_btn = ttk.Button(
            btn_center,
            text="✅ Kích hoạt",
            command=self.activate_key,
            width=20
        )
        activate_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(
            btn_center,
            text="❌ Hủy",
            command=self.cancel,
            width=20
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
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

