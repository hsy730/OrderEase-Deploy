"""
字段解析工具模块 - 自动处理多种命名格式 (PascalCase/camelCase/snake_case)
"""

from typing import Any, Dict, List, Optional, Union


class FieldResolver:
    """字段解析器 - 自动处理多种命名格式"""

    # 常见字段的命名变体映射
    FIELD_VARIANTS = {
        "id": ["ID", "id", "Id"],
        "shop_id": ["shopId", "shop_id", "ShopID", "ShopId"],
        "product_id": ["productId", "product_id", "ProductID", "ProductId"],
        "order_id": ["orderId", "order_id", "OrderID", "OrderId"],
        "user_id": ["userId", "user_id", "UserID", "UserId"],
        "tag_id": ["tagId", "tag_id", "TagID", "TagId"],
        "image_url": ["imageUrl", "image_url", "ImageURL", "ImageUrl"],
        "owner_username": ["owner_username", "ownerUsername", "OwnerUsername"],
        "contact_phone": ["contact_phone", "contactPhone", "ContactPhone"],
        "created_at": ["createdAt", "created_at", "CreatedAt"],
        "updated_at": ["updatedAt", "updated_at", "UpdatedAt"],
    }

    # 常见容器的命名变体映射
    CONTAINER_VARIANTS = {
        "data": ["data", "Data"],
        "items": ["items", "Items"],
        "users": ["users", "Users"],
        "products": ["products", "Products"],
        "orders": ["orders", "Orders"],
        "tags": ["tags", "Tags"],
        "shops": ["shops", "Shops"],
    }

    @classmethod
    def get_field(cls, data: Dict, field_name: str, default: Any = None) -> Any:
        """从字典中获取字段值，自动尝试多种命名格式

        Args:
            data: 源数据字典
            field_name: 字段名称（使用标准命名）
            default: 默认值

        Returns:
            字段值，如果找不到则返回默认值

        Examples:
            >>> data = {"shopId": 123, "productName": "test"}
            >>> FieldResolver.get_field(data, "shop_id")
            123
            >>> FieldResolver.get_field(data, "product_name")
            'test'
        """
        if not isinstance(data, dict):
            return default

        # 直接匹配
        if field_name in data:
            return data[field_name]

        # 尝试已知变体
        variants = cls.FIELD_VARIANTS.get(field_name, [])
        for variant in variants:
            if variant in data:
                return data[variant]

        # 尝试 PascalCase (首字母大写)
        pascal_case = field_name.replace("_", " ").title().replace(" ", "")
        if pascal_case in data:
            return data[pascal_case]

        # 尝试 camelCase (首字母小写)
        camel_case = field_name[0] + field_name[1:].replace("_", " ").title().replace(" ", "")
        if camel_case in data:
            return data[camel_case]

        return default

    @classmethod
    def get_nested_field(cls, data: Dict, field_path: str, default: Any = None) -> Any:
        """获取嵌套字段值，支持点号分隔的路径

        Args:
            data: 源数据字典
            field_path: 字段路径，如 "data.user.id"
            default: 默认值

        Returns:
            字段值，如果找不到则返回默认值

        Examples:
            >>> data = {"data": {"shopId": 123}}
            >>> FieldResolver.get_nested_field(data, "data.shop_id")
            123
        """
        if not isinstance(data, dict):
            return default

        keys = field_path.split(".")
        value = data

        for key in keys:
            if not isinstance(value, dict):
                return default
            value = cls.get_field(value, key, default)
            if value is default:
                return default

        return value

    @classmethod
    def extract_id(cls, data: Union[Dict, List]) -> Optional[Any]:
        """从响应数据中提取ID，支持多种格式

        Args:
            data: 响应数据（字典或列表）

        Returns:
            ID值，如果找不到则返回None

        Examples:
            >>> FieldResolver.extract_id({"id": 123})
            123
            >>> FieldResolver.extract_id({"ID": 456})
            456
            >>> FieldResolver.extract_id({"data": {"productId": 789}})
            789
        """
        if isinstance(data, list):
            return None

        if not isinstance(data, dict):
            return None

        # 尝试顶层ID字段
        for key in ["ID", "id", "Id"]:
            if key in data:
                value = data[key]
                # 如果值是字典，递归查找
                if isinstance(value, dict):
                    return cls.extract_id(value)
                return value

        # 尝试从data中提取
        if "data" in data:
            data_value = data["data"]
            if isinstance(data_value, dict):
                return cls.extract_id(data_value)

        # 尝试特定类型的ID
        for id_type in ["order_id", "shop_id", "product_id", "user_id", "tag_id"]:
            value = cls.get_field(data, id_type)
            if value is not None:
                return value

        return None

    @classmethod
    def get_list(cls, data: Dict, list_name: str, default: List = None) -> List:
        """获取列表字段，自动尝试多种命名格式

        Args:
            data: 源数据字典
            list_name: 列表字段名称（使用标准命名）
            default: 默认值

        Returns:
            列表值，如果找不到则返回默认值

        Examples:
            >>> data = {"products": [{"id": 1}]}
            >>> FieldResolver.get_list(data, "products")
            [{'id': 1}]
            >>> data = {"Products": [{"id": 2}]}
            >>> FieldResolver.get_list(data, "products")
            [{'id': 2}]
        """
        if default is None:
            default = []

        value = cls.get_field(data, list_name)
        if value is None:
            # 尝试容器变体
            variants = cls.CONTAINER_VARIANTS.get(list_name, [])
            for variant in variants:
                if variant in data:
                    value = data[variant]
                    break

        if isinstance(value, list):
            return value

        return default

    @classmethod
    def find_field_value(cls, data: Dict, search_key: str, default: Any = None) -> Any:
        """在嵌套结构中查找指定键的值（深度优先搜索）

        Args:
            data: 源数据字典
            search_key: 要查找的键名
            default: 默认值

        Returns:
            找到的值，如果找不到则返回默认值

        Examples:
            >>> data = {"shop": {"info": {"shopId": 123}}}
            >>> FieldResolver.find_field_value(data, "shopId")
            123
        """
        if not isinstance(data, dict):
            return default

        # 检查当前层级
        if search_key in data:
            return data[search_key]

        # 递归搜索
        for key, value in data.items():
            if isinstance(value, dict):
                result = cls.find_field_value(value, search_key, default)
                if result is not default:
                    return result

        return default

    @classmethod
    def normalize_keys(cls, data: Dict, to_snake_case: bool = True) -> Dict:
        """规范化字典的键名格式

        Args:
            data: 源数据字典
            to_snake_case: True表示转为snake_case，False表示转为camelCase

        Returns:
            键名规范化后的新字典

        Examples:
            >>> data = {"shopId": 123, "productName": "test"}
            >>> FieldResolver.normalize_keys(data, to_snake_case=True)
            {'shop_id': 123, 'product_name': 'test'}
        """
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            new_key = key

            if to_snake_case:
                # camelCase/PascalCase -> snake_case
                import re
                new_key = re.sub('([A-Z]+)', r'_\1', key).lower().lstrip('_')
            else:
                # snake_case -> camelCase
                parts = key.split('_')
                new_key = parts[0] + ''.join(p.title() for p in parts[1:])

            # 递归处理嵌套字典
            if isinstance(value, dict):
                result[new_key] = cls.normalize_keys(value, to_snake_case)
            elif isinstance(value, list):
                result[new_key] = [
                    cls.normalize_keys(item, to_snake_case) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[new_key] = value

        return result
