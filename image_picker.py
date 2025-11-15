"""
Module chụp và lưu hình ảnh từ màn hình
"""
import os
from PIL import ImageGrab
from datetime import datetime
from typing import Tuple, Optional


class ImagePicker:
    def __init__(self, save_directory: str = "images"):
        """
        Khởi tạo ImagePicker
        :param save_directory: Thư mục lưu ảnh
        """
        self.save_directory = save_directory
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Đảm bảo thư mục tồn tại"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def capture_region(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """
        Chụp vùng màn hình và lưu
        :param x1, y1: Điểm bắt đầu
        :param x2, y2: Điểm kết thúc
        :return: Đường dẫn file đã lưu
        """
        # Đảm bảo x1 < x2 và y1 < y2
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Chụp màn hình
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        
        # Tạo tên file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(self.save_directory, filename)
        
        # Lưu ảnh
        screenshot.save(filepath)
        return filepath
    
    def capture_full_screen(self) -> str:
        """Chụp toàn màn hình và lưu"""
        screenshot = ImageGrab.grab()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.save_directory, filename)
        screenshot.save(filepath)
        return filepath
    
    def capture_around_point(self, x: int, y: int, width: int = 100, height: int = 100) -> str:
        """
        Chụp vùng xung quanh một điểm
        :param x, y: Tọa độ trung tâm
        :param width, height: Kích thước vùng
        :return: Đường dẫn file đã lưu
        """
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = x + width // 2
        bottom = y + height // 2
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"point_{x}_{y}_{timestamp}.png"
        filepath = os.path.join(self.save_directory, filename)
        screenshot.save(filepath)
        return filepath

