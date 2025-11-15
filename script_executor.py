"""
Module thực thi script tự động với if-else và điều kiện
Giống AutoMouse - hỗ trợ if-else, tìm hình ảnh, kiểm tra cửa sổ
Không sử dụng Windows API
"""
import time
import cv2
import numpy as np
from PIL import ImageGrab
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from typing import List, Dict, Any, Optional, Tuple
import re
import os


class ScriptExecutor:
    def __init__(self, image_finder=None):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.is_running = False
        self.image_finder = image_finder
        self.if_stack = []  # Stack để xử lý if-else lồng nhau
        self.condition_result = True  # Kết quả điều kiện hiện tại
        
    def parse_script(self, script_text: str) -> List[Dict[str, Any]]:
        """
        Parse script text thành danh sách các hành động
        Hỗ trợ if-else, tìm hình ảnh, kiểm tra cửa sổ
        """
        actions = []
        lines = script_text.strip().split('\n')
        if_stack = []  # Stack để theo dõi if-else blocks
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_num = i + 1
            
            # Bỏ qua comment và dòng trống
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Xử lý if-else-endif
            if line.lower().startswith('if '):
                condition = self._parse_condition(line[3:].strip())
                if_stack.append({
                    'type': 'if',
                    'condition': condition,
                    'line': line_num,
                    'executed': False
                })
                actions.append({
                    'type': 'if_start',
                    'condition': condition,
                    'line': line_num
                })
                
            elif line.lower() == 'else':
                if if_stack:
                    if_stack[-1]['type'] = 'if-else'
                actions.append({
                    'type': 'else',
                    'line': line_num
                })
                
            elif line.lower() in ['endif', 'end if']:
                if if_stack:
                    if_stack.pop()
                actions.append({
                    'type': 'endif',
                    'line': line_num
                })
                
            else:
                # Parse command thông thường
                parts = line.split()
                if not parts:
                    i += 1
                    continue
                
                cmd = parts[0].lower()
                
                try:
                    action = self._parse_command(cmd, parts, line_num)
                    if action:
                        actions.append(action)
                except Exception as e:
                    raise ValueError(f"Line {line_num}: {str(e)}")
            
            i += 1
        
        return actions
    
    def _parse_condition(self, condition_text: str) -> Dict[str, Any]:
        """Parse điều kiện if"""
        condition_text = condition_text.strip().lower()
        
        # If image found
        if 'image' in condition_text or 'picture' in condition_text:
            # Format: if image "path" found
            match = re.search(r'["\']([^"\']+)["\']', condition_text)
            if match:
                return {
                    'type': 'image_found',
                    'image_path': match.group(1)
                }
        
        # If window exists/appears
        if 'window' in condition_text:
            # Format: if window "title" exists/appears
            match = re.search(r'["\']([^"\']+)["\']', condition_text)
            if match:
                return {
                    'type': 'window_exists',
                    'window_title': match.group(1)
                }
        
        # If position/region
        if 'region' in condition_text or 'position' in condition_text:
            # Format: if found in region [x,y widthxheight]
            match = re.search(r'\[(\d+),(\d+)\s+(\d+)x(\d+)\]', condition_text)
            if match:
                return {
                    'type': 'region_check',
                    'x': int(match.group(1)),
                    'y': int(match.group(2)),
                    'width': int(match.group(3)),
                    'height': int(match.group(4))
                }
        
        # Default: luôn true
        return {'type': 'always_true'}
    
    def _parse_command(self, cmd: str, parts: List[str], line_num: int) -> Optional[Dict[str, Any]]:
        """Parse một lệnh"""
        if cmd == 'click':
            if len(parts) < 3:
                raise ValueError("click requires x y [delay]")
            x, y = int(parts[1]), int(parts[2])
            delay = float(parts[3]) if len(parts) > 3 else 0.1
            return {'type': 'click', 'x': x, 'y': y, 'delay': delay, 'line': line_num}
            
        elif cmd == 'move':
            if len(parts) < 3:
                raise ValueError("move requires x y [delay]")
            x, y = int(parts[1]), int(parts[2])
            delay = float(parts[3]) if len(parts) > 3 else 0.1
            return {'type': 'move', 'x': x, 'y': y, 'delay': delay, 'line': line_num}
            
        elif cmd == 'wait' or cmd == 'delay':
            if len(parts) < 2:
                raise ValueError("wait requires seconds")
            seconds = float(parts[1])
            return {'type': 'wait', 'seconds': seconds, 'line': line_num}
            
        elif cmd == 'key' or cmd == 'keystroke':
            if len(parts) < 2:
                raise ValueError("key requires keyname [delay]")
            keyname = ' '.join(parts[1:]) if '+' in parts[1] else parts[1]
            delay = float(parts[-1]) if len(parts) > 2 and parts[-1].replace('.', '').isdigit() else 0.1
            return {'type': 'key', 'key': keyname, 'delay': delay, 'line': line_num}
            
        elif cmd == 'rightclick':
            if len(parts) < 3:
                raise ValueError("rightclick requires x y [delay]")
            x, y = int(parts[1]), int(parts[2])
            delay = float(parts[3]) if len(parts) > 3 else 0.1
            return {'type': 'rightclick', 'x': x, 'y': y, 'delay': delay, 'line': line_num}
            
        elif cmd == 'doubleclick':
            if len(parts) < 3:
                raise ValueError("doubleclick requires x y [delay]")
            x, y = int(parts[1]), int(parts[2])
            delay = float(parts[3]) if len(parts) > 3 else 0.1
            return {'type': 'doubleclick', 'x': x, 'y': y, 'delay': delay, 'line': line_num}
            
        elif cmd == 'type' or cmd == 'typetext':
            # Format: type "text" [delay]
            text_match = re.search(r'["\']([^"\']+)["\']', ' '.join(parts[1:]))
            if text_match:
                text = text_match.group(1)
                delay = float(parts[-1]) if len(parts) > 2 and parts[-1].replace('.', '').isdigit() else 0.05
                return {'type': 'type', 'text': text, 'delay': delay, 'line': line_num}
            else:
                raise ValueError("type requires text in quotes")
        
        elif cmd == 'findimage' or cmd == 'find_image':
            # Format: findimage "path" [x] [y] [width] [height]
            match = re.search(r'["\']([^"\']+)["\']', ' '.join(parts[1:]))
            if match:
                image_path = match.group(1)
                region = None
                if len(parts) >= 6:
                    region = (int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]))
                return {'type': 'findimage', 'image_path': image_path, 'region': region, 'line': line_num}
            else:
                raise ValueError("findimage requires image path in quotes")
        
        elif cmd == 'scroll':
            if len(parts) < 4:
                raise ValueError("scroll requires x y dx dy")
            x, y, dx, dy = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
            return {'type': 'scroll', 'x': x, 'y': y, 'dx': dx, 'dy': dy, 'line': line_num}
        
        elif cmd == 'keyhold' or cmd == 'key_hold':
            if len(parts) < 3:
                raise ValueError("keyhold requires key duration")
            key_name = parts[1]
            duration = float(parts[2])
            return {'type': 'key_hold', 'key': key_name, 'duration': duration, 'line': line_num}
        
        elif cmd == 'keypress' or cmd == 'key_press':
            if len(parts) < 2:
                raise ValueError("keypress requires key")
            key_name = parts[1]
            return {'type': 'key_press', 'key': key_name, 'line': line_num}
        
        elif cmd == 'keyrelease' or cmd == 'key_release':
            if len(parts) < 2:
                raise ValueError("keyrelease requires key")
            key_name = parts[1]
            return {'type': 'key_release', 'key': key_name, 'line': line_num}
        
        return None
    
    def execute_actions(self, actions: List[Dict[str, Any]], loop: bool = False, callback=None):
        """Thực thi danh sách hành động với hỗ trợ if-else"""
        self.is_running = True
        self.if_stack = []
        
        try:
            while self.is_running:
                i = 0
                while i < len(actions):
                    if not self.is_running:
                        break
                    
                    action = actions[i]
                    action_type = action.get('type')
                    
                    # Xử lý if-else
                    if action_type == 'if_start':
                        condition_result = self._evaluate_condition(action['condition'])
                        self.if_stack.append({
                            'condition': condition_result,
                            'executed': condition_result,
                            'in_else': False
                        })
                        if not condition_result:
                            # Bỏ qua đến else hoặc endif
                            i = self._skip_to_else_or_endif(actions, i)
                        i += 1
                        continue
                    
                    elif action_type == 'else':
                        if self.if_stack:
                            if_stack_item = self.if_stack[-1]
                            if if_stack_item['executed']:
                                # Đã thực thi if, bỏ qua else
                                i = self._skip_to_endif(actions, i)
                            else:
                                # Chưa thực thi if, thực thi else
                                if_stack_item['in_else'] = True
                                if_stack_item['executed'] = True
                        i += 1
                        continue
                    
                    elif action_type == 'endif':
                        if self.if_stack:
                            self.if_stack.pop()
                        i += 1
                        continue
                    
                    # Kiểm tra xem có đang trong if block không được thực thi
                    if self.if_stack and not self.if_stack[-1]['executed']:
                        i += 1
                        continue
                    
                    # Thực thi hành động
                    self._execute_action(action, callback)
                    i += 1
                
                if not loop:
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.is_running = False
    
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """Đánh giá điều kiện"""
        cond_type = condition.get('type')
        
        if cond_type == 'image_found':
            if self.image_finder:
                image_path = condition.get('image_path')
                if os.path.exists(image_path):
                    position = self.image_finder.find_image(image_path)
                    return position is not None
            return False
        
        elif cond_type == 'window_exists':
            # Kiểm tra cửa sổ có tồn tại không
            try:
                import pygetwindow as gw
                window_title = condition.get('window_title')
                windows = gw.getWindowsWithTitle(window_title)
                return len(windows) > 0
            except:
                return False
        
        elif cond_type == 'region_check':
            # Kiểm tra vùng (có thể mở rộng sau)
            return True
        
        elif cond_type == 'always_true':
            return True
        
        return False
    
    def _skip_to_else_or_endif(self, actions: List[Dict[str, Any]], start_idx: int) -> int:
        """Bỏ qua đến else hoặc endif"""
        depth = 1
        i = start_idx + 1
        while i < len(actions) and depth > 0:
            action_type = actions[i].get('type')
            if action_type == 'if_start':
                depth += 1
            elif action_type == 'else' and depth == 1:
                return i
            elif action_type == 'endif':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return i
    
    def _skip_to_endif(self, actions: List[Dict[str, Any]], start_idx: int) -> int:
        """Bỏ qua đến endif"""
        depth = 1
        i = start_idx + 1
        while i < len(actions) and depth > 0:
            action_type = actions[i].get('type')
            if action_type == 'if_start':
                depth += 1
            elif action_type == 'endif':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return i
    
    def _execute_action(self, action: Dict[str, Any], callback=None):
        """Thực thi một hành động - tiêm trực tiếp vào chuột và bàn phím"""
        action_type = action.get('type')
        
        if callback:
            callback(f"Executing: {action_type}")
        
        if action_type == 'click':
            self.mouse.position = (action['x'], action['y'])
            time.sleep(0.01)
            self.mouse.click(Button.left, 1)
            time.sleep(action.get('delay', 0.1))
            
        elif action_type == 'rightclick':
            self.mouse.position = (action['x'], action['y'])
            time.sleep(0.01)
            self.mouse.click(Button.right, 1)
            time.sleep(action.get('delay', 0.1))
            
        elif action_type == 'doubleclick':
            self.mouse.position = (action['x'], action['y'])
            time.sleep(0.01)
            self.mouse.click(Button.left, 2)
            time.sleep(action.get('delay', 0.1))
            
        elif action_type == 'move':
            self._smooth_move(action['x'], action['y'])
            time.sleep(action.get('delay', 0.1))
            
        elif action_type == 'wait':
            time.sleep(action['seconds'])
            
        elif action_type == 'key':
            self._press_key(action['key'])
            time.sleep(action.get('delay', 0.1))
        
        elif action_type == 'key_press':
            # Nhấn phím (tiêm trực tiếp vào bàn phím) - không thả
            self._press_key_only(action['key'], callback)
            time.sleep(action.get('delay', 0.1))
        
        elif action_type == 'key_release':
            # Thả phím (tiêm trực tiếp vào bàn phím)
            self._release_key_only(action['key'], callback)
            time.sleep(action.get('delay', 0.1))
        
        elif action_type == 'key_hold':
            # Giữ phím trong một khoảng thời gian (tiêm trực tiếp vào bàn phím)
            key_name = action['key']
            duration = action.get('duration', 1.0)
            self._hold_key(key_name, duration, callback)
            time.sleep(0.1)
            
        elif action_type == 'type':
            self._type_text(action['text'], action.get('delay', 0.05))
            
        elif action_type == 'findimage':
            if self.image_finder:
                position = self.image_finder.find_image(
                    action['image_path'],
                    action.get('region')
                )
                if position:
                    # Tự động click vào hình ảnh tìm thấy
                    self.mouse.position = position
                    time.sleep(0.01)
                    self.mouse.click(Button.left, 1)
            
        elif action_type == 'scroll':
            self.mouse.position = (action['x'], action['y'])
            self.mouse.scroll(action['dx'], action['dy'])
    
    def _press_key(self, key_str: str):
        """Nhấn phím"""
        try:
            # Xử lý phím kết hợp như "Ctrl+A", "Shift+E"
            if '+' in key_str:
                keys = [k.strip() for k in key_str.split('+')]
                modifiers = []
                main_key = keys[-1]
                
                for mod in keys[:-1]:
                    mod_lower = mod.lower()
                    if mod_lower == 'ctrl':
                        modifiers.append(Key.ctrl)
                    elif mod_lower == 'alt':
                        modifiers.append(Key.alt)
                    elif mod_lower == 'shift':
                        modifiers.append(Key.shift)
                
                # Nhấn modifiers
                for mod in modifiers:
                    self.keyboard.press(mod)
                
                # Nhấn phím chính
                key_map = {
                    'enter': Key.enter,
                    'space': Key.space,
                    'tab': Key.tab,
                    'esc': Key.esc,
                    'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e',
                    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
                    'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o',
                    'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
                    'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z'
                }
                
                main_key_obj = key_map.get(main_key.lower(), main_key)
                if isinstance(main_key_obj, str):
                    self.keyboard.type(main_key_obj)
                else:
                    self.keyboard.press(main_key_obj)
                    self.keyboard.release(main_key_obj)
                
                # Thả modifiers
                for mod in reversed(modifiers):
                    self.keyboard.release(mod)
            else:
                # Phím đơn
                key_map = {
                    'enter': Key.enter,
                    'space': Key.space,
                    'tab': Key.tab,
                    'esc': Key.esc,
                    'backspace': Key.backspace,
                    'delete': Key.delete,
                    'up': Key.up,
                    'down': Key.down,
                    'left': Key.left,
                    'right': Key.right,
                }
                
                key_obj = key_map.get(key_str.lower(), key_str)
                if isinstance(key_obj, str):
                    self.keyboard.type(key_obj)
                else:
                    self.keyboard.press(key_obj)
                    self.keyboard.release(key_obj)
        except Exception as e:
            if callback:
                callback(f"Error pressing key {key_str}: {e}")
    
    def _parse_key_name(self, key_str: str):
        """Parse tên phím thành Key object"""
        key_str = key_str.lower().strip()
        
        # Special keys
        special_keys = {
            'ctrl': Key.ctrl, 'ctrl_l': Key.ctrl_l, 'ctrl_r': Key.ctrl_r,
            'alt': Key.alt, 'alt_l': Key.alt_l, 'alt_r': Key.alt_r,
            'shift': Key.shift, 'shift_l': Key.shift_l, 'shift_r': Key.shift_r,
            'enter': Key.enter, 'space': Key.space, 'tab': Key.tab,
            'esc': Key.esc, 'escape': Key.esc,
            'backspace': Key.backspace, 'delete': Key.delete,
            'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
            'home': Key.home, 'end': Key.end,
            'page_up': Key.page_up, 'page_down': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }
        
        if key_str in special_keys:
            return special_keys[key_str]
        
        # Regular character
        if len(key_str) == 1:
            return key_str
        
        return None
    
    def _press_key_only(self, key_str: str, callback=None):
        """Chỉ nhấn phím (không thả) - tiêm trực tiếp vào bàn phím"""
        try:
            key = self._parse_key_name(key_str)
            if key:
                self.keyboard.press(key)
        except Exception as e:
            if callback:
                callback(f"Error pressing key {key_str}: {e}")
    
    def _release_key_only(self, key_str: str, callback=None):
        """Chỉ thả phím - tiêm trực tiếp vào bàn phím"""
        try:
            key = self._parse_key_name(key_str)
            if key:
                self.keyboard.release(key)
        except Exception as e:
            if callback:
                callback(f"Error releasing key {key_str}: {e}")
    
    def _hold_key(self, key_str: str, duration: float, callback=None):
        """Giữ phím trong một khoảng thời gian - tiêm trực tiếp vào bàn phím"""
        try:
            key = self._parse_key_name(key_str)
            if key:
                self.keyboard.press(key)
                time.sleep(duration)
                self.keyboard.release(key)
        except Exception as e:
            if callback:
                callback(f"Error holding key {key_str}: {e}")
    
    def _type_text(self, text: str, delay: float = 0.05):
        """Gõ text"""
        for char in text:
            self.keyboard.type(char)
            time.sleep(delay)
    
    def _smooth_move(self, target_x: int, target_y: int, steps: int = 10):
        """Di chuyển chuột mượt mà"""
        current_x, current_y = self.mouse.position
        for i in range(steps + 1):
            if not self.is_running:
                break
            progress = i / steps
            eased_progress = progress * (2 - progress)
            new_x = int(current_x + (target_x - current_x) * eased_progress)
            new_y = int(current_y + (target_y - current_y) * eased_progress)
            self.mouse.position = (new_x, new_y)
            time.sleep(0.001)
    
    def stop(self):
        """Dừng thực thi script"""
        self.is_running = False
