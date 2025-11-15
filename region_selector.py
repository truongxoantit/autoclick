"""
Module chọn vùng màn hình để chụp ảnh
"""
import tkinter as tk
from PIL import ImageGrab
from typing import Optional, Tuple


class RegionSelector:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.canvas = None
        self.overlay = None
        self.selected = False
        
    def select_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Hiển thị overlay để chọn vùng màn hình
        :return: (x1, y1, x2, y2) hoặc None nếu hủy
        """
        # Tạo cửa sổ fullscreen trong suốt
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='black')
        
        # Canvas để vẽ
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.overlay.bind('<Escape>', lambda e: self.cancel())
        
        # Chờ người dùng chọn
        self.overlay.wait_window()
        
        if self.selected:
            return (self.start_x, self.start_y, self.end_x, self.end_y)
        return None
    
    def on_press(self, event):
        """Bắt đầu chọn vùng"""
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.end_x = event.x_root
        self.end_y = event.y_root
        
    def on_drag(self, event):
        """Kéo để chọn vùng"""
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.draw_rectangle()
        
    def on_release(self, event):
        """Kết thúc chọn vùng"""
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.selected = True
        self.overlay.destroy()
        
    def draw_rectangle(self):
        """Vẽ hình chữ nhật chọn vùng"""
        if self.rect:
            self.canvas.delete(self.rect)
        
        # Chuyển đổi tọa độ màn hình sang tọa độ canvas
        x1 = min(self.start_x, self.end_x) - self.overlay.winfo_rootx()
        y1 = min(self.start_y, self.end_y) - self.overlay.winfo_rooty()
        x2 = max(self.start_x, self.end_x) - self.overlay.winfo_rootx()
        y2 = max(self.start_y, self.end_y) - self.overlay.winfo_rooty()
        
        self.rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='red', width=3, fill='blue', stipple='gray25'
        )
        
    def cancel(self):
        """Hủy chọn"""
        self.selected = False
        self.overlay.destroy()

