"""
Module phát lại các thao tác đã ghi lại
Sử dụng pynput để mô phỏng click như người dùng thật
Tiêm trực tiếp vào chuột và bàn phím, không dùng Windows API
"""
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from typing import List, Dict, Any


class ActionPlayer:
    def __init__(self, speed_multiplier: float = 1.0):
        """
        Khởi tạo ActionPlayer
        :param speed_multiplier: Hệ số tốc độ (1.0 = bình thường, 2.0 = nhanh gấp đôi)
        """
        self.speed_multiplier = speed_multiplier
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.is_playing = False
        self.current_action_index = 0
        self.held_keys = set()  # Tập hợp các phím đang được giữ
        
    def play_actions(self, actions: List[Dict[str, Any]], loop: bool = False):
        """
        Phát lại các thao tác
        :param actions: Danh sách các thao tác đã ghi
        :param loop: True để lặp lại liên tục
        """
        if not actions:
            print("Không có thao tác nào để phát lại")
            return
        
        self.is_playing = True
        
        try:
            while self.is_playing:
                self.current_action_index = 0
                last_time = 0
                
                for action in actions:
                    if not self.is_playing:
                        break
                    
                    # Tính thời gian chờ
                    current_time = action.get('time', 0)
                    delay = (current_time - last_time) / self.speed_multiplier
                    if delay > 0:
                        time.sleep(delay)
                    
                    # Thực hiện thao tác
                    self._execute_action(action)
                    last_time = current_time
                
                if not loop:
                    break
                    
        except KeyboardInterrupt:
            print("Đã dừng phát lại")
        finally:
            self.is_playing = False
            self.current_action_index = 0
    
    def _execute_action(self, action: Dict[str, Any]):
        """Thực hiện một thao tác"""
        action_type = action.get('type', '')
        x = action.get('x', 0)
        y = action.get('y', 0)
        
        if action_type == 'move':
            # Di chuyển chuột mượt mà
            self._smooth_move(x, y)
            
        elif action_type == 'press_left':
            self.mouse.position = (x, y)
            time.sleep(0.01)  # Nhỏ delay để giống người thật
            self.mouse.press(Button.left)
            
        elif action_type == 'release_left':
            self.mouse.position = (x, y)
            time.sleep(0.01)
            self.mouse.release(Button.left)
            
        elif action_type == 'press_right':
            self.mouse.position = (x, y)
            time.sleep(0.01)
            self.mouse.press(Button.right)
            
        elif action_type == 'release_right':
            self.mouse.position = (x, y)
            time.sleep(0.01)
            self.mouse.release(Button.right)
            
        elif action_type == 'scroll':
            dx = action.get('dx', 0)
            dy = action.get('dy', 0)
            self.mouse.position = (x, y)
            self.mouse.scroll(dx, dy)
        
        # Xử lý phím bàn phím
        elif action_type == 'key_press':
            key_name = action.get('key', '')
            self._press_key(key_name)
            
        elif action_type == 'key_release':
            key_name = action.get('key', '')
            self._release_key(key_name)
            
        elif action_type == 'key_hold':
            key_name = action.get('key', '')
            duration = action.get('duration', 1.0)
            self._hold_key(key_name, duration)
        
        self.current_action_index += 1
    
    def _press_key(self, key_name: str):
        """Nhấn phím (tiêm trực tiếp vào bàn phím)"""
        try:
            key = self._parse_key(key_name)
            if key:
                self.keyboard.press(key)
                self.held_keys.add(key_name)
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
    
    def _release_key(self, key_name: str):
        """Thả phím (tiêm trực tiếp vào bàn phím)"""
        try:
            key = self._parse_key(key_name)
            if key:
                self.keyboard.release(key)
                self.held_keys.discard(key_name)
        except Exception as e:
            print(f"Error releasing key {key_name}: {e}")
    
    def _hold_key(self, key_name: str, duration: float):
        """Giữ phím trong một khoảng thời gian"""
        try:
            key = self._parse_key(key_name)
            if key:
                self.keyboard.press(key)
                self.held_keys.add(key_name)
                time.sleep(duration)
                self.keyboard.release(key)
                self.held_keys.discard(key_name)
        except Exception as e:
            print(f"Error holding key {key_name}: {e}")
    
    def _parse_key(self, key_name: str):
        """Parse tên phím thành Key object"""
        key_name = key_name.lower().strip()
        
        # Special keys
        special_keys = {
            'ctrl': Key.ctrl,
            'ctrl_l': Key.ctrl_l,
            'ctrl_r': Key.ctrl_r,
            'alt': Key.alt,
            'alt_l': Key.alt_l,
            'alt_r': Key.alt_r,
            'shift': Key.shift,
            'shift_l': Key.shift_l,
            'shift_r': Key.shift_r,
            'enter': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'esc': Key.esc,
            'escape': Key.esc,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }
        
        if key_name in special_keys:
            return special_keys[key_name]
        
        # Regular character
        if len(key_name) == 1:
            return key_name
        
        return None
    
    def release_all_keys(self):
        """Thả tất cả các phím đang được giữ"""
        for key_name in list(self.held_keys):
            try:
                self._release_key(key_name)
            except:
                pass
        self.held_keys.clear()
    
    def _smooth_move(self, target_x: int, target_y: int, steps: int = 10):
        """
        Di chuyển chuột mượt mà đến vị trí đích
        Sử dụng để mô phỏng di chuyển tự nhiên hơn
        """
        current_x, current_y = self.mouse.position
        
        for i in range(steps + 1):
            if not self.is_playing:
                break
                
            progress = i / steps
            # Sử dụng easing function để di chuyển mượt mà
            eased_progress = progress * (2 - progress)  # Ease-out
            
            new_x = int(current_x + (target_x - current_x) * eased_progress)
            new_y = int(current_y + (target_y - current_y) * eased_progress)
            
            self.mouse.position = (new_x, new_y)
            time.sleep(0.001)  # Nhỏ delay giữa các bước
    
    def stop(self):
        """Dừng phát lại và thả tất cả phím đang giữ"""
        self.is_playing = False
        self.release_all_keys()

