"""
数据导出接口测试 - 覆盖数据导出功能

注意：
- 导出接口返回ZIP文件（包含所有表的CSV）
- 导入接口会清空所有表后重新导入（危险操作），已移至手动测试

测试接口：
- GET /admin/data/export - 导出所有数据为ZIP
"""

import pytest
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import API_BASE_URL, make_request_with_retry


class TestDataExport:
    """数据导出接口测试"""

    def test_export_all_data(self, admin_token):
        """测试导出所有数据（ZIP格式）"""
        url = f"{API_BASE_URL}/admin/data/export"
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"导出数据失败: {response.text}"

        # 验证响应是ZIP文件
        content_type = response.headers.get("Content-Type", "")
        assert "zip" in content_type or "application/octet-stream" in content_type, \
            f"响应应为ZIP文件，实际Content-Type: {content_type}"

        # 验证响应内容不为空
        assert len(response.content) > 0, "导出的ZIP文件为空"

        # 验证是否为有效的ZIP文件
        import zipfile
        try:
            with zipfile.ZipFile(__import__('io').BytesIO(response.content)) as zf:
                # ZIP文件应包含多个CSV文件
                namelist = zf.namelist()
                assert len(namelist) > 0, "ZIP文件中没有文件"
                print(f"✓ 导出成功，包含 {len(namelist)} 个文件: {namelist[:5]}...")
        except zipfile.BadZipFile:
            pytest.fail("响应内容不是有效的ZIP文件")

        print(f"✓ 导出所有数据成功，文件大小: {len(response.content)} bytes")

    def test_export_response_headers(self, admin_token):
        """测试导出响应头信息"""
        url = f"{API_BASE_URL}/admin/data/export"
        headers = {"Authorization": f"Bearer {admin_token}"}

        def request_func():
            return requests.get(url, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 200, f"导出失败: {response.text}"

        # 检查Content-Disposition头
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition.lower(), \
            f"应有Content-Disposition头，实际: {content_disposition}"
        assert ".zip" in content_disposition, \
            f"文件名应以.zip结尾，实际: {content_disposition}"

        print(f"✓ 响应头正确: {content_disposition}")

    def test_export_without_auth(self):
        """测试未认证时导出（应失败）"""
        url = f"{API_BASE_URL}/admin/data/export"

        def request_func():
            return requests.get(url)

        response = make_request_with_retry(request_func)
        assert response.status_code in [401, 403], \
            f"未认证请求应返回401或403，实际: {response.status_code}"
        print("✓ 未认证访问被正确拒绝")


class TestDataImportWarning:
    """
    数据导入接口警告性说明

    ⚠️ 重要提示：
    /admin/data/import 接口会执行以下危险操作：
    1. 清空所有数据库表（admins, shops, users, products, orders等）
    2. 从上传的ZIP文件重新导入所有数据
    3. 这是一个破坏性操作，会导致所有现有数据丢失！

    因此，此接口不适合在自动化测试中运行。
    如需测试，请：
    - 使用独立的测试环境
    - 手动执行并验证
    - 或使用备份的环境快照恢复
    """

    def test_import_requires_zip_file(self, admin_token):
        """测试导入需要ZIP文件（不实际执行导入）"""
        url = f"{API_BASE_URL}/admin/data/import"
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 测试不提供文件时的情况
        def request_func():
            return requests.post(url, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, \
            f"缺少文件时应返回400，实际: {response.status_code}"
        print("✓ 缺少文件时正确返回400错误")

    def test_import_rejects_non_zip_file(self, admin_token):
        """测试拒绝非ZIP文件"""
        url = f"{API_BASE_URL}/admin/data/import"
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 尝试上传文本文件（非ZIP）
        files = {'file': ('test.txt', 'not a zip file', 'text/plain')}

        def request_func():
            return requests.post(url, files=files, headers=headers)

        response = make_request_with_retry(request_func)
        assert response.status_code == 400, \
            f"非ZIP文件应被拒绝(400)，实际: {response.status_code}"
        print("✓ 非ZIP文件被正确拒绝")

    def test_import_warning_documentation(self):
        """文档化导入接口的危险性"""
        warning_msg = """
        ╔══════════════════════════════════════════════════╗
        ║  ⚠️  /admin/data/import 接口安全警告          ║
        ╠══════════════════════════════════════════════════╣
        ║                                                  ║
        ║  此接口会执行以下操作：                          ║
        ║  1. 删除所有现有数据                            ║
        ║  2. 从ZIP文件导入新数据                         ║
        ║  3. 操作不可逆                                  ║
        ║                                                  ║
        ⚠️  请勿在自动化测试或生产环境使用！              ║
        ║  仅限开发环境的手动测试                           ║
        ╚══════════════════════════════════════════════════╝
        """
        print(warning_msg)
        assert True  # 这是一个文档化的测试用例
