"""
用户头像接口测试模块

测试范围:
- 头像上传接口 (POST /user/upload-avatar)
- 头像获取接口 (GET /user/avatar)
"""

import os
import sys
import pytest
import requests
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestUserAvatarUpload:
    """用户头像上传接口测试类"""

    @pytest.fixture
    def valid_image_file(self, tmp_path):
        """创建有效的测试图片文件"""
        # 创建一个简单的 1x1 像素的 PNG 图片
        import base64
        
        # 最小的有效 PNG 图片 (1x1 像素, 透明)
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        )
        
        image_file = tmp_path / "test_avatar.png"
        image_file.write_bytes(png_data)
        return str(image_file)

    @pytest.fixture
    def large_image_file(self, tmp_path):
        """创建超过 5MB 的测试图片文件"""
        # 创建一个较大的文件 (6MB)
        image_file = tmp_path / "large_avatar.jpg"
        image_file.write_bytes(b'0' * (6 * 1024 * 1024))
        return str(image_file)

    @pytest.fixture
    def invalid_file(self, tmp_path):
        """创建无效的文件类型"""
        invalid_file = tmp_path / "test.exe"
        invalid_file.write_text("This is not an image")
        return str(invalid_file)

    def test_upload_avatar_success(self, frontend_user_token, valid_image_file):
        """测试成功上传头像"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        
        with open(valid_image_file, 'rb') as f:
            files = {'avatar': ('avatar.png', f, 'image/png')}
            headers = {'Authorization': f'Bearer {frontend_user_token}'}
            
            def request_func():
                return requests.post(url, files=files, headers=headers)
            
            response = make_request_with_retry(request_func)
        
        assert response.status_code == 200, f"上传头像应该返回200，实际返回: {response.status_code}, 响应: {response.text}"

        data = response.json()
        assert 'avatar_url' in data, f"响应应该包含 avatar_url 字段，实际响应: {data}"
        assert data['avatar_url'].startswith('/uploads/avatars/'), f"avatar_url 应该以 /uploads/avatars/ 开头，实际: {data['avatar_url']}"

    def test_upload_avatar_without_token(self, valid_image_file):
        """测试未授权上传头像"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        
        with open(valid_image_file, 'rb') as f:
            files = {'avatar': ('avatar.png', f, 'image/png')}
            
            def request_func():
                return requests.post(url, files=files)
            
            response = make_request_with_retry(request_func)
        
        assert response.status_code == 401, f"未授权上传应该返回401，实际返回: {response.status_code}"

    def test_upload_avatar_with_invalid_token(self, valid_image_file):
        """测试使用无效 token 上传头像"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        
        with open(valid_image_file, 'rb') as f:
            files = {'avatar': ('avatar.png', f, 'image/png')}
            headers = {'Authorization': 'Bearer invalid_token'}
            
            def request_func():
                return requests.post(url, files=files, headers=headers)
            
            response = make_request_with_retry(request_func)
        
        assert response.status_code == 401, f"无效 token 上传应该返回401，实际返回: {response.status_code}"

    def test_upload_avatar_without_file(self, frontend_user_token):
        """测试不上传文件"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        def request_func():
            return requests.post(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 400, f"不上传文件应该返回400，实际返回: {response.status_code}"

    def test_upload_avatar_invalid_format(self, frontend_user_token, invalid_file):
        """测试上传无效格式的文件"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        
        with open(invalid_file, 'rb') as f:
            files = {'avatar': ('test.exe', f, 'application/octet-stream')}
            headers = {'Authorization': f'Bearer {frontend_user_token}'}
            
            def request_func():
                return requests.post(url, files=files, headers=headers)
            
            response = make_request_with_retry(request_func)
        
        assert response.status_code == 400, f"上传无效格式应该返回400，实际返回: {response.status_code}"

    def test_upload_avatar_too_large(self, frontend_user_token, large_image_file):
        """测试上传超过 5MB 的文件"""
        url = f"{API_BASE_URL}/user/upload-avatar"
        
        with open(large_image_file, 'rb') as f:
            files = {'avatar': ('large.jpg', f, 'image/jpeg')}
            headers = {'Authorization': f'Bearer {frontend_user_token}'}
            
            def request_func():
                return requests.post(url, files=files, headers=headers)
            
            response = make_request_with_retry(request_func)
        
        assert response.status_code == 400, f"上传过大文件应该返回400，实际返回: {response.status_code}"


class TestUserAvatarGet:
    """用户头像获取接口测试类"""

    @pytest.fixture
    def uploaded_avatar_url(self, frontend_user_token):
        """上传一个头像并返回 URL"""
        import base64
        import tempfile
        
        # 创建临时图片文件
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        )
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            temp_file = f.name
        
        try:
            # 上传头像
            url = f"{API_BASE_URL}/user/upload-avatar"
            with open(temp_file, 'rb') as f:
                files = {'avatar': ('avatar.png', f, 'image/png')}
                headers = {'Authorization': f'Bearer {frontend_user_token}'}
                
                def request_func():
                    return requests.post(url, files=files, headers=headers)
                
                response = make_request_with_retry(request_func)
            
            assert response.status_code == 200, f"上传头像失败: {response.text}"
            data = response.json()
            return data['avatar_url']
        finally:
            os.unlink(temp_file)

    def test_get_avatar_success(self, frontend_user_token, uploaded_avatar_url):
        """测试成功获取头像"""
        # 从 URL 中提取文件名
        filename = uploaded_avatar_url.replace('/uploads/avatars/', '')
        
        url = f"{API_BASE_URL}/user/avatar"
        params = {'path': filename}
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 200, f"获取头像应该返回200，实际返回: {response.status_code}"
        assert response.headers.get('content-type', '').startswith('image/'), \
            f"响应应该是图片类型，实际 Content-Type: {response.headers.get('content-type')}"

    def test_get_avatar_without_token(self, uploaded_avatar_url):
        """测试未授权获取头像"""
        filename = uploaded_avatar_url.replace('/uploads/avatars/', '')
        
        url = f"{API_BASE_URL}/user/avatar"
        params = {'path': filename}
        
        def request_func():
            return requests.get(url, params=params)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 401, f"未授权获取应该返回401，实际返回: {response.status_code}"

    def test_get_avatar_with_invalid_token(self, uploaded_avatar_url):
        """测试使用无效 token 获取头像"""
        filename = uploaded_avatar_url.replace('/uploads/avatars/', '')
        
        url = f"{API_BASE_URL}/user/avatar"
        params = {'path': filename}
        headers = {'Authorization': 'Bearer invalid_token'}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 401, f"无效 token 获取应该返回401，实际返回: {response.status_code}"

    def test_get_avatar_without_path(self, frontend_user_token):
        """测试不带 path 参数获取头像"""
        url = f"{API_BASE_URL}/user/avatar"
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        def request_func():
            return requests.get(url, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 400, f"不带 path 应该返回400，实际返回: {response.status_code}"

    def test_get_avatar_with_empty_path(self, frontend_user_token):
        """测试使用空 path 参数获取头像"""
        url = f"{API_BASE_URL}/user/avatar"
        params = {'path': ''}
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 400, f"空 path 应该返回400，实际返回: {response.status_code}"

    def test_get_avatar_not_found(self, frontend_user_token):
        """测试获取不存在的头像"""
        url = f"{API_BASE_URL}/user/avatar"
        # 使用符合格式但不存在的文件名: {随机字符串}_{时间戳}.{扩展名}
        params = {'path': 'aBcDeFgHiJ_1234567890123.png'}
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        def request_func():
            return requests.get(url, params=params, headers=headers)
        
        response = make_request_with_retry(request_func)
        
        assert response.status_code == 404, f"不存在的头像应该返回404，实际返回: {response.status_code}"

    def test_get_avatar_invalid_path_format(self, frontend_user_token):
        """测试使用无效格式的 path 获取头像"""
        url = f"{API_BASE_URL}/user/avatar"
        
        invalid_paths = [
            '../../../etc/passwd',  # 路径遍历攻击
            'avatar.png;rm -rf /',  # 命令注入
            '<script>alert(1)</script>',  # XSS
            'avatar.png\x00.jpg',  # 空字节攻击
        ]
        
        for invalid_path in invalid_paths:
            params = {'path': invalid_path}
            headers = {'Authorization': f'Bearer {frontend_user_token}'}
            
            def request_func():
                return requests.get(url, params=params, headers=headers)
            
            response = make_request_with_retry(request_func)
            
            assert response.status_code in [400, 404], \
                f"无效 path '{invalid_path}' 应该返回400或404，实际返回: {response.status_code}"

    def test_get_avatar_with_directory_traversal(self, frontend_user_token):
        """测试目录遍历攻击防护"""
        url = f"{API_BASE_URL}/user/avatar"
        
        traversal_paths = [
            '../config.yaml',
            '..\\\windows\\\system32\\\config\\\sam',
            '....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2fetc/passwd',  # URL 编码
        ]
        
        for path in traversal_paths:
            params = {'path': path}
            headers = {'Authorization': f'Bearer {frontend_user_token}'}
            
            def request_func():
                return requests.get(url, params=params, headers=headers)
            
            response = make_request_with_retry(request_func)
            
            assert response.status_code in [400, 404], \
                f"目录遍历路径 '{path}' 应该返回400或404，实际返回: {response.status_code}"


class TestUserAvatarIntegration:
    """用户头像集成测试类"""

    def test_upload_and_get_avatar_flow(self, frontend_user_token):
        """测试完整的上传和获取头像流程"""
        import base64
        import tempfile
        
        # 1. 创建测试图片
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        )
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            temp_file = f.name
        
        try:
            # 2. 上传头像
            upload_url = f"{API_BASE_URL}/user/upload-avatar"
            with open(temp_file, 'rb') as f:
                files = {'avatar': ('avatar.png', f, 'image/png')}
                headers = {'Authorization': f'Bearer {frontend_user_token}'}
                
                def upload_request():
                    return requests.post(upload_url, files=files, headers=headers)
                
                upload_response = make_request_with_retry(upload_request)
            
            assert upload_response.status_code == 200, f"上传失败: {upload_response.text}"
            avatar_url = upload_response.json()['avatar_url']
            
            # 3. 获取头像
            filename = avatar_url.replace('/uploads/avatars/', '')
            get_url = f"{API_BASE_URL}/user/avatar"
            params = {'path': filename}
            
            def get_request():
                return requests.get(get_url, params=params, headers=headers)
            
            get_response = make_request_with_retry(get_request)
            
            assert get_response.status_code == 200, f"获取头像失败: {get_response.status_code}"
            
            # 4. 验证返回的图片数据
            assert len(get_response.content) > 0, "返回的图片数据不应该为空"
            
        finally:
            os.unlink(temp_file)

    def test_upload_new_avatar_replaces_old(self, frontend_user_token):
        """测试上传新头像会替换旧头像"""
        import base64
        import tempfile
        
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        )
        
        headers = {'Authorization': f'Bearer {frontend_user_token}'}
        
        # 上传第一个头像
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            temp_file1 = f.name
        
        try:
            upload_url = f"{API_BASE_URL}/user/upload-avatar"
            with open(temp_file1, 'rb') as f:
                files = {'avatar': ('avatar1.png', f, 'image/png')}
                
                def upload_request1():
                    return requests.post(upload_url, files=files, headers=headers)
                
                response1 = make_request_with_retry(upload_request1)
            
            assert response1.status_code == 200
            first_avatar_url = response1.json()['avatar_url']
            first_filename = first_avatar_url.replace('/uploads/avatars/', '')
            
            # 上传第二个头像
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(png_data)
                temp_file2 = f.name
            
            try:
                with open(temp_file2, 'rb') as f:
                    files = {'avatar': ('avatar2.png', f, 'image/png')}
                    
                    def upload_request2():
                        return requests.post(upload_url, files=files, headers=headers)
                    
                    response2 = make_request_with_retry(upload_request2)
                
                assert response2.status_code == 200
                second_avatar_url = response2.json()['avatar_url']
                second_filename = second_avatar_url.replace('/uploads/avatars/', '')
                
                # 验证两个头像 URL 不同
                assert first_avatar_url != second_avatar_url, "新头像 URL 应该与旧的不同"
                
                # 验证旧头像已不存在（被删除）
                get_url = f"{API_BASE_URL}/user/avatar"
                params = {'path': first_filename}
                
                def get_old_request():
                    return requests.get(get_url, params=params, headers=headers)
                
                old_response = make_request_with_retry(get_old_request)
                
                # 旧头像应该返回 404（已被删除）
                assert old_response.status_code == 404, \
                    f"旧头像应该返回404，实际返回: {old_response.status_code}"
                
            finally:
                os.unlink(temp_file2)
        finally:
            os.unlink(temp_file1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
