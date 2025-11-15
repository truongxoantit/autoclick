"""
Module quản lý key license với GitHub
- Kiểm tra key theo thời gian thực từ GitHub
- Quản lý thời gian hết hạn
- Mỗi máy chỉ dùng 1 key
- Tự động đóng ứng dụng nếu key hết hạn
- Tự động đăng ký máy lên GitHub
"""
import os
import json
import hashlib
import platform
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import tkinter.messagebox as messagebox
from auto_registration import AutoRegistration


class KeyManager:
    def __init__(self, github_repo: str = "truongxoantit/autoclick", key_file: str = "license.key", auto_register: bool = True):
        """
        Khởi tạo KeyManager
        :param github_repo: Repository GitHub chứa keys (format: username/repo)
        :param key_file: File lưu key local
        :param auto_register: Tự động đăng ký máy lên GitHub khi khởi động
        """
        self.github_repo = github_repo
        self.key_file = key_file
        self.keys_url = f"https://raw.githubusercontent.com/{github_repo}/main/keys.json"
        self.machine_id = self._get_machine_id()
        self.current_key = None
        self.key_data = None
        
        # Tự động đăng ký máy lên GitHub
        if auto_register:
            self.auto_registration = AutoRegistration(github_repo=github_repo)
            self._auto_register_machine()
        
    def _get_machine_id(self) -> str:
        """Lấy ID duy nhất của máy"""
        # Lấy thông tin máy tính
        machine_info = f"{platform.node()}{platform.system()}{platform.processor()}"
        # Tạo hash từ thông tin máy
        machine_id = hashlib.md5(machine_info.encode()).hexdigest()
        return machine_id
    
    def _auto_register_machine(self):
        """Tự động đăng ký máy lên GitHub"""
        try:
            if hasattr(self, 'auto_registration'):
                if not self.auto_registration.is_registered():
                    # Đăng ký máy mới
                    if self.auto_registration.register_machine():
                        print(f"Machine {self.machine_id} đã được đăng ký tự động lên GitHub")
                    else:
                        print(f"Không thể đăng ký máy lên GitHub (có thể do không có quyền ghi)")
                else:
                    print(f"Machine {self.machine_id} đã được đăng ký trước đó")
        except Exception as e:
            print(f"Lỗi khi đăng ký tự động: {e}")
    
    def _load_local_key(self) -> Optional[Dict[str, Any]]:
        """Đọc key từ file local"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _save_local_key(self, key_data: Dict[str, Any]):
        """Lưu key vào file local"""
        try:
            with open(self.key_file, 'w', encoding='utf-8') as f:
                json.dump(key_data, f, indent=2)
        except Exception as e:
            print(f"Error saving key: {e}")
    
    def _fetch_keys_from_github(self) -> Optional[Dict[str, Any]]:
        """Lấy danh sách keys từ GitHub"""
        try:
            response = requests.get(self.keys_url, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch keys: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching keys from GitHub: {e}")
            return None
    
    def _validate_key(self, key: str, keys_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Kiểm tra key có hợp lệ không"""
        if not keys_data or 'keys' not in keys_data:
            return None
        
        for key_info in keys_data['keys']:
            if key_info.get('key') == key:
                # Kiểm tra thời gian hết hạn
                expire_date = datetime.fromisoformat(key_info.get('expire_date', '2000-01-01'))
                if datetime.now() > expire_date:
                    return None  # Key đã hết hạn
                
                # Kiểm tra machine_id
                registered_machine = key_info.get('machine_id')
                if registered_machine and registered_machine != self.machine_id:
                    return None  # Key đã được dùng trên máy khác
                
                return key_info
        
        return None
    
    def register_key(self, key: str) -> bool:
        """
        Đăng ký key mới
        :param key: Key license
        :return: True nếu thành công
        """
        # Lấy keys từ GitHub
        keys_data = self._fetch_keys_from_github()
        if not keys_data:
            messagebox.showerror("Error", "Không thể kết nối với GitHub để kiểm tra key!")
            return False
        
        # Kiểm tra key
        key_info = self._validate_key(key, keys_data)
        if not key_info:
            messagebox.showerror("Invalid Key", "Key không hợp lệ, đã hết hạn hoặc đã được sử dụng trên máy khác!")
            return False
        
        # Lưu key local
        key_data = {
            'key': key,
            'machine_id': self.machine_id,
            'key_name': key_info.get('key_name', 'Unknown'),
            'expire_date': key_info.get('expire_date'),
            'registered_date': datetime.now().isoformat()
        }
        self._save_local_key(key_data)
        self.current_key = key
        self.key_data = key_data
        
        messagebox.showinfo("Success", f"Key '{key_info.get('key_name')}' đã được kích hoạt thành công!")
        return True
    
    def check_key(self) -> bool:
        """
        Kiểm tra key hiện tại có hợp lệ không
        :return: True nếu key hợp lệ
        """
        # Đọc key local
        local_key_data = self._load_local_key()
        if not local_key_data:
            return False
        
        # Kiểm tra machine_id
        if local_key_data.get('machine_id') != self.machine_id:
            return False  # Key không thuộc máy này
        
        # Kiểm tra thời gian hết hạn
        expire_date_str = local_key_data.get('expire_date')
        if expire_date_str:
            try:
                expire_date = datetime.fromisoformat(expire_date_str)
                if datetime.now() > expire_date:
                    return False  # Key đã hết hạn
            except:
                return False
        
        # Kiểm tra với GitHub (optional, có thể bỏ qua nếu không có internet)
        keys_data = self._fetch_keys_from_github()
        if keys_data:
            key_info = self._validate_key(local_key_data.get('key'), keys_data)
            if not key_info:
                return False
        
        self.current_key = local_key_data.get('key')
        self.key_data = local_key_data
        return True
    
    def get_key_info(self) -> Optional[Dict[str, Any]]:
        """Lấy thông tin key hiện tại"""
        if self.key_data:
            return {
                'key_name': self.key_data.get('key_name', 'Unknown'),
                'expire_date': self.key_data.get('expire_date', 'N/A'),
                'days_remaining': self._get_days_remaining()
            }
        return None
    
    def _get_days_remaining(self) -> int:
        """Tính số ngày còn lại"""
        if not self.key_data or not self.key_data.get('expire_date'):
            return 0
        
        try:
            expire_date = datetime.fromisoformat(self.key_data.get('expire_date'))
            remaining = (expire_date - datetime.now()).days
            return max(0, remaining)
        except:
            return 0
    
    def is_expired(self) -> bool:
        """Kiểm tra key có hết hạn không"""
        return not self.check_key()
    
    def get_machine_id(self) -> str:
        """Lấy machine ID"""
        return self.machine_id

