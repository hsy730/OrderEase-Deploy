import os
import re

handlers_dir = r"d:\local_code_repo\OrderEase-Golang\src\handlers"

def fix_response_type():
    """修复 swagger 注释中的 Response 类型"""
    for file in os.listdir(handlers_dir):
        if file.endswith('.go') and file not in ['handlers.go', 'sse_test.html']:
            file_path = os.path.join(handlers_dir, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            # 替换 Response 为 map[string]interface{}
            content = re.sub(r'\{object\}\s+Response', '{object} map[string]interface{}', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {file}")

if __name__ == "__main__":
    fix_response_type()
    print("Done!")
