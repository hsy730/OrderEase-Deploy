import os
import re

handlers_dir = r"d:\local_code_repo\OrderEase-Golang\src\handlers"
routes_backend_dir = r"d:\local_code_repo\OrderEase-Golang\src\routes\backend"
routes_frontend_dir = r"d:\local_code_repo\OrderEase-Golang\src\routes\frontend"

def extract_swagger_from_routes():
    """从 routes 目录提取 swagger 注释"""
    swagger_map = {}
    
    for root, dirs, files in os.walk(routes_backend_dir):
        for file in files:
            if file.endswith('.go'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找所有 swagger 注释块
                pattern = r'(/\*\*[\s\S]*?\*/\s*group\.(GET|POST|PUT|DELETE|PATCH)\s*\([^)]+\)\s*"([^"]+)"\s*,\s*h\.(\w+)\))'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    comment_block, method, path, handler_name = match
                    # 提取 swagger 注释
                    swagger_pattern = r'(/\*\*[\s\S]*?\*/)'
                    swagger_match = re.search(swagger_pattern, comment_block)
                    if swagger_match:
                        swagger_text = swagger_match.group(0)
                        # 清理注释
                        swagger_text = re.sub(r'@Router\s+/api/', '@Router /api/', swagger_text)
                        swagger_map[handler_name] = swagger_text
    
    for root, dirs, files in os.walk(routes_frontend_dir):
        for file in files:
            if file.endswith('.go'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                pattern = r'(/\*\*[\s\S]*?\*/\s*group\.(GET|POST|PUT|DELETE|PATCH)\s*\([^)]+\)\s*"([^"]+)"\s*,\s*h\.(\w+)\))'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    comment_block, method, path, handler_name = match
                    swagger_pattern = r'(/\*\*[\s\S]*?\*/)'
                    swagger_match = re.search(swagger_pattern, comment_block)
                    if swagger_match:
                        swagger_text = swagger_match.group(0)
                        swagger_text = re.sub(r'@Router\s+/api/', '@Router /api/', swagger_text)
                        swagger_map[handler_name] = swagger_text
    
    return swagger_map

def add_swagger_to_handlers():
    """将 swagger 注释添加到 handlers 文件中"""
    swagger_map = extract_swagger_from_routes()
    
    for file in os.listdir(handlers_dir):
        if file.endswith('.go') and file not in ['handlers.go', 'sse_test.html']:
            file_path = os.path.join(handlers_dir, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 查找所有的 handler 函数
            pattern = r'func\s+\(h\s+\*Handler\)\s+(\w+)\s*\([^)]*\)\s*\{'
            matches = list(re.finditer(pattern, content))
            
            # 从后往前替换，避免位置偏移
            for match in reversed(matches):
                handler_name = match.group(1)
                if handler_name in swagger_map:
                    swagger_text = swagger_map[handler_name]
                    # 在函数定义前添加 swagger 注释
                    new_content = content[:match.start()] + '\n' + swagger_text + '\n' + content[match.start():]
                    content = new_content
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {file} ({len(re.findall(pattern, original_content))} handlers)")

if __name__ == "__main__":
    add_swagger_to_handlers()
    print("Done!")
