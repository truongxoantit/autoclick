"""
Module phát lại các thao tác đã ghi lại
Sử dụng pynput để mô phỏng click như người dùng thật
"""
import time
from pynput.mouse import Button, Controller as MouseController
from typing import List, Dict, Any


class ActionPlayer:
    def __init__(self, speed_multiplier: float = 1.0):
        """
        Khởi tạo ActionPlayer
        :param speed_multiplier: Hệ số tốc độ (1.0 = bình thường, 2.0 = nhanh gấp đôi)
        """
        self.speed_multiplier = speed_multiplier
        self.mouse = MouseController()
        self.is_playing = False
        self.current_action_index = 0
        
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
        
        self.current_action_index += 1
    
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
        """Dừng phát lại"""
        self.is_playing = False

