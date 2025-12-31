import os
import re

files_to_update = [
    'auth/test_login.py',
    'auth/test_logout.py',
    'auth/test_refresh_token.py',
    'auth/test_temp_login.py',
    'admin/test_base.py',
    'admin/test_order.py',
    'admin/test_product.py',
    'admin/test_shop.py',
    'admin/test_tag.py',
    'admin/test_user.py',
    'shop_owner/test_base.py',
    'shop_owner/test_order.py',
    'shop_owner/test_product.py',
    'shop_owner/test_shop.py',
    'shop_owner/test_tag.py',
    'shop_owner/test_user.py',
    'frontend/test_auth.py',
    'frontend/test_order.py',
    'frontend/test_product.py',
    'frontend/test_shop.py'
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'password: "Admin@123456"', '"password": "Admin@123456"', content)
        content = re.sub(r'old_password: "Admin@123456"', '"old_password": "Admin@123456"', content)
        content = re.sub(r'new_password: "Admin@123456"', '"new_password": "Admin@123456"', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {file_path}')
    else:
        print(f'Not found: {file_path}')

print('Done!')
