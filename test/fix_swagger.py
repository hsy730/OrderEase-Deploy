import os
import re

routes_dir = r"d:\local_code_repo\OrderEase-Golang\src\routes"

for root, dirs, files in os.walk(routes_dir):
    for file in files:
        if file.endswith('.go'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            content = content.replace('@Produce', '@Produce')
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {file_path}")
            else:
                print(f"No changes: {file_path}")

print("Done!")
