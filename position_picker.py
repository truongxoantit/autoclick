"""
Module pick vị trí chuột với overlay hiển thị tọa độ
Bấm Ctrl để pick vị trí
"""
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Listener as MouseListener
from pynput import keyboard
import threading


class PositionPicker:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.overlay = None
        self.canvas = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_picking = False
        
    def pick_position(self, callback=None):
        """
        Bắt đầu pick vị trí
        :param callback: Hàm callback khi pick xong (x, y)
        :return: (x, y) hoặc None
        """
        self.result = None
        self.is_picking = True
        
        # Ẩn cửa sổ chính
        self.parent.withdraw()
        
        # Tạo overlay fullscreen
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='black')
        self.overlay.overrideredirect(True)
        
        # Canvas để vẽ
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='black', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Label hiển thị tọa độ
        self.coord_label = tk.Label(
            self.overlay,
            text="Di chuyển chuột và nhấn Ctrl để pick vị trí | ESC để hủy",
            font=("Arial", 14, "bold"),
            bg='black',
            fg='yellow',
            anchor='n'
        )
        self.coord_label.pack(fill=tk.X, pady=10)
        
        # Label hiển thị tọa độ hiện tại
        self.pos_label = tk.Label(
            self.overlay,
            text="X: 0, Y: 0",
            font=("Consolas", 16, "bold"),
            bg='black',
            fg='lime',
            anchor='center'
        )
        self.pos_label.pack(fill=tk.X, pady=5)
        
        # Bind events
        self.overlay.bind('<Escape>', lambda e: self.cancel())
        
        # Bắt đầu lắng nghe chuột và bàn phím
        self.start_listeners()
        
        # Chờ kết quả
        self.overlay.wait_window()
        
        # Khôi phục cửa sổ chính
        self.parent.deiconify()
        
        if callback and self.result:
            callback(self.result[0], self.result[1])
        
        return self.result
    
    def start_listeners(self):
        """Bắt đầu lắng nghe chuột và bàn phím"""
        # Lắng nghe chuột để cập nhật tọa độ
        def on_move(x, y):
            if self.is_picking and self.pos_label:
                self.pos_label.config(text=f"X: {x}, Y: {y}")
        
        # Lắng nghe bàn phím để pick vị trí
        def on_press(key):
            try:
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    # Lấy vị trí chuột hiện tại
                    from pynput.mouse import Controller
                    mouse = Controller()
                    x, y = mouse.position
                    self.result = (x, y)
                    self.is_picking = False
                    self.overlay.destroy()
            except:
                pass
        
        def on_release(key):
            try:
                if key == keyboard.Key.esc:
                    self.cancel()
            except:
                pass
        
        # Chạy listeners trong thread riêng
        def start_mouse_listener():
            try:
                self.mouse_listener = MouseListener(on_move=on_move)
                self.mouse_listener.start()
                self.mouse_listener.join()
            except Exception as e:
                print(f"Error in mouse listener: {e}")
        
        def start_keyboard_listener():
            try:
                self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
                self.keyboard_listener.start()
                self.keyboard_listener.join()
            except Exception as e:
                print(f"Error in keyboard listener: {e}")
        
        # Start listeners
        threading.Thread(target=start_mouse_listener, daemon=True).start()
        threading.Thread(target=start_keyboard_listener, daemon=True).start()
    
    def cancel(self):
        """Hủy pick"""
        self.is_picking = False
        self.result = None
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.overlay:
            self.overlay.destroy()

