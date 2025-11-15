"""
Module tự động đăng ký máy lên GitHub khi mở ứng dụng lần đầu
"""
import os
import json
import hashlib
import platform
import requests
from datetime import datetime
from typing import Optional, Dict, Any


class AutoRegistration:
    def __init__(self, github_repo: str = "truongxoantit/autoclick", github_token: str = None):
        """
        Khởi tạo AutoRegistration
        :param github_repo: Repository GitHub (format: username/repo)
        :param github_token: GitHub Personal Access Token (optional, có thể dùng public repo)
        """
        self.github_repo = github_repo
        self.github_token = github_token
        self.registration_file = "registrations.json"
        self.registration_url = f"https://api.github.com/repos/{github_repo}/contents/{self.registration_file}"
        self.raw_url = f"https://raw.githubusercontent.com/{github_repo}/main/{self.registration_file}"
        self.machine_id = self._get_machine_id()
        
    def _get_machine_id(self) -> str:
        """Lấy ID duy nhất của máy"""
        machine_info = f"{platform.node()}{platform.system()}{platform.processor()}"
        machine_id = hashlib.md5(machine_info.encode()).hexdigest()
        return machine_id
    
    def _get_machine_info(self) -> Dict[str, Any]:
        """Lấy thông tin máy"""
        return {
            'machine_id': self.machine_id,
            'computer_name': platform.node(),
            'system': platform.system(),
            'processor': platform.processor(),
            'platform': platform.platform(),
            'registration_date': datetime.now().isoformat(),
            'status': 'pending',  # pending, approved, rejected
            'expire_date': None,
            'key_name': None,
        }
    
    def _get_file_sha(self) -> Optional[str]:
        """Lấy SHA của file trên GitHub (để update)"""
        try:
            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            response = requests.get(self.registration_url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get('sha')
            return None
        except:
            return None
    
    def _create_registration_file(self, content: str, sha: Optional[str] = None) -> bool:
        """Tạo hoặc update file registration trên GitHub"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            data = {
                'message': f'Auto registration: {self.machine_id}',
                'content': content,
            }
            
            if sha:
                data['sha'] = sha
            
            response = requests.put(self.registration_url, headers=headers, json=data, timeout=10)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error creating registration file: {e}")
            return False
    
    def register_machine(self) -> bool:
        """
        Tự động đăng ký máy lên GitHub
        :return: True nếu thành công
        """
        # Kiểm tra xem đã đăng ký chưa
        if self.is_registered():
            return True
        
        # Lấy thông tin máy
        machine_info = self._get_machine_info()
        
        # Đọc file registrations hiện tại từ GitHub
        registrations = self._get_existing_registrations()
        
        # Thêm thông tin máy mới
        if 'machines' not in registrations:
            registrations['machines'] = []
        
        # Kiểm tra xem machine_id đã tồn tại chưa
        existing = next((m for m in registrations['machines'] if m.get('machine_id') == self.machine_id), None)
        if existing:
            return True  # Đã đăng ký rồi
        
        registrations['machines'].append(machine_info)
        
        # Convert sang JSON và encode base64
        import base64
        content_json = json.dumps(registrations, indent=2, ensure_ascii=False)
        content_base64 = base64.b64encode(content_json.encode('utf-8')).decode('utf-8')
        
        # Lấy SHA nếu file đã tồn tại
        sha = self._get_file_sha()
        
        # Tạo/update file trên GitHub
        if self._create_registration_file(content_base64, sha):
            return True
        
        return False
    
    def _get_existing_registrations(self) -> Dict[str, Any]:
        """Lấy danh sách đăng ký hiện tại từ GitHub"""
        try:
            response = requests.get(self.raw_url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {'machines': []}
    
    def is_registered(self) -> bool:
        """Kiểm tra xem máy đã đăng ký chưa"""
        try:
            registrations = self._get_existing_registrations()
            if 'machines' in registrations:
                return any(m.get('machine_id') == self.machine_id for m in registrations['machines'])
        except:
            pass
        return False
    
    def get_registration_status(self) -> Optional[Dict[str, Any]]:
        """Lấy trạng thái đăng ký của máy"""
        try:
            registrations = self._get_existing_registrations()
            if 'machines' in registrations:
                machine = next((m for m in registrations['machines'] if m.get('machine_id') == self.machine_id), None)
                return machine
        except:
            pass
        return None
    
    def get_machine_id(self) -> str:
        """Lấy machine ID"""
        return self.machine_id

