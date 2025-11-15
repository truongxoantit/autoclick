"""
Module ghi lại thao tác người dùng (click, di chuyển chuột)
Sử dụng pynput để ghi lại các sự kiện chuột ở mức thấp
"""
import json
import time
from datetime import datetime
from pynput import mouse
from typing import List, Dict, Any


class ActionRecorder:
    def __init__(self):
        self.actions: List[Dict[str, Any]] = []
        self.is_recording = False
        self.start_time = None
        self.mouse_listener = None
        
    def start_recording(self):
        """Bắt đầu ghi lại thao tác"""
        self.actions = []
        self.is_recording = True
        self.start_time = time.time()
        
        # Tạo listener cho chuột
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.mouse_listener.start()
        print("Đã bắt đầu ghi lại thao tác...")
        
    def stop_recording(self):
        """Dừng ghi lại thao tác"""
        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        print(f"Đã dừng ghi lại. Tổng cộng {len(self.actions)} thao tác.")
        
    def _on_move(self, x, y):
        """Ghi lại di chuyển chuột"""
        if not self.is_recording:
            return
            
        current_time = time.time() - self.start_time
        self.actions.append({
            'type': 'move',
            'x': x,
            'y': y,
            'time': current_time
        })
        
    def _on_click(self, x, y, button, pressed):
        """Ghi lại click chuột"""
        if not self.is_recording:
            return
            
        current_time = time.time() - self.start_time
        action_type = 'press' if pressed else 'release'
        button_name = 'left' if button == mouse.Button.left else 'right'
        
        self.actions.append({
            'type': f'{action_type}_{button_name}',
            'x': x,
            'y': y,
            'time': current_time
        })
        
    def _on_scroll(self, x, y, dx, dy):
        """Ghi lại cuộn chuột"""
        if not self.is_recording:
            return
            
        current_time = time.time() - self.start_time
        self.actions.append({
            'type': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'time': current_time
        })
        
    def save_to_file(self, filename: str):
        """Lưu các thao tác vào file JSON"""
        data = {
            'created_at': datetime.now().isoformat(),
            'total_actions': len(self.actions),
            'actions': self.actions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Đã lưu {len(self.actions)} thao tác vào {filename}")
        
    def load_from_file(self, filename: str):
        """Tải các thao tác từ file JSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.actions = data.get('actions', [])
        print(f"Đã tải {len(self.actions)} thao tác từ {filename}")
        return self.actions

