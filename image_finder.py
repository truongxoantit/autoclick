"""
Module tìm kiếm hình ảnh trên màn hình và click vào đó
Sử dụng OpenCV để tìm kiếm template matching
"""
import cv2
import numpy as np
from PIL import ImageGrab
from typing import Tuple, Optional, List
import time


class ImageFinder:
    def __init__(self, confidence: float = 0.8):
        """
        Khởi tạo ImageFinder
        :param confidence: Độ chính xác tối thiểu để tìm thấy hình ảnh (0.0 - 1.0)
        Không sử dụng Windows API, chỉ dùng PIL để chụp màn hình
        """
        self.confidence = confidence
        
    def find_image(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        Tìm hình ảnh trên màn hình
        :param template_path: Đường dẫn đến file hình ảnh cần tìm
        :param region: Vùng tìm kiếm (x, y, width, height), None = toàn màn hình
        :return: Tọa độ (x, y) của hình ảnh nếu tìm thấy, None nếu không
        """
        try:
            # Chụp màn hình không dùng Windows API
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Đọc template
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"Không thể đọc file hình ảnh: {template_path}")
                return None
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Kiểm tra độ chính xác
            if max_val >= self.confidence:
                # Tính tọa độ trung tâm của hình ảnh
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                print(f"Tìm thấy hình ảnh tại ({center_x}, {center_y}) với độ chính xác {max_val:.2%}")
                return (center_x, center_y)
            else:
                print(f"Không tìm thấy hình ảnh. Độ chính xác cao nhất: {max_val:.2%}")
                return None
                
        except Exception as e:
            print(f"Lỗi khi tìm kiếm hình ảnh: {e}")
            return None
    
    def find_and_click(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None, 
                      button: str = 'left', delay: float = 0.1) -> bool:
        """
        Tìm hình ảnh và click vào đó
        :param template_path: Đường dẫn đến file hình ảnh cần tìm
        :param region: Vùng tìm kiếm
        :param button: 'left' hoặc 'right'
        :param delay: Thời gian chờ trước khi click (giây)
        :return: True nếu tìm thấy và click thành công, False nếu không
        """
        position = self.find_image(template_path, region)
        if position:
            time.sleep(delay)
            # Sử dụng pynput thay vì pyautogui
            from pynput.mouse import Button, Controller
            mouse = Controller()
            mouse.position = (position[0], position[1])
            time.sleep(0.01)
            if button == 'left':
                mouse.click(Button.left, 1)
            else:
                mouse.click(Button.right, 1)
            print(f"Đã click vào ({position[0]}, {position[1]})")
            return True
        return False
    
    def find_all_occurrences(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None, 
                            threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        Tìm tất cả các vị trí xuất hiện của hình ảnh
        :param template_path: Đường dẫn đến file hình ảnh cần tìm
        :param region: Vùng tìm kiếm
        :param threshold: Ngưỡng độ chính xác
        :return: Danh sách các tọa độ (x, y)
        """
        positions = []
        try:
            # Chụp màn hình không dùng Windows API
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Đọc template
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                return positions
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            h, w = template.shape
            for pt in zip(*locations[::-1]):
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2
                
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                positions.append((center_x, center_y))
            
            # Loại bỏ các vị trí trùng lặp gần nhau
            positions = self._remove_duplicates(positions, w, h)
            
        except Exception as e:
            print(f"Lỗi khi tìm tất cả hình ảnh: {e}")
        
        return positions
    
    def _remove_duplicates(self, positions: List[Tuple[int, int]], width: int, height: int) -> List[Tuple[int, int]]:
        """Loại bỏ các vị trí trùng lặp gần nhau"""
        if not positions:
            return []
        
        filtered = [positions[0]]
        for pos in positions[1:]:
            is_duplicate = False
            for existing in filtered:
                distance = np.sqrt((pos[0] - existing[0])**2 + (pos[1] - existing[1])**2)
                if distance < min(width, height) * 0.5:
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered.append(pos)
        
        return filtered

