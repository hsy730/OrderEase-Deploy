import pytest
import sys


def main():
    """
    OrderEase API 测试主入口文件
    
    用法:
        python main.py                    # 运行所有测试
        python main.py --module auth        # 运行认证模块测试
        python main.py --module frontend     # 运行前端模块测试
        python main.py --module admin        # 运行管理员模块测试
        python main.py --module shop_owner   # 运行商家模块测试
        python main.py --verbose            # 显示详细输出
    """
    args = sys.argv[1:]
    
    if not args or args[0] == "--help" or args[0] == "-h":
        print(__doc__)
        return 0
    
    module = None
    verbose = False
    
    for i, arg in enumerate(args):
        if arg == "--module" and i + 1 < len(args):
            module = args[i + 1]
        elif arg in ["--verbose", "-v"]:
            verbose = True
    
    test_files = []
    
    if module == "auth":
        test_files = ["test_auth.py"]
        print("运行认证模块测试...")
    elif module == "frontend":
        test_files = ["test_frontend.py"]
        print("运行前端模块测试...")
    elif module == "admin":
        test_files = [
            "test_admin_base.py",
            "test_admin_shop.py",
            "test_admin_product.py",
            "test_admin_user.py",
            "test_admin_order.py",
            "test_admin_tag.py",
            "test_admin_data.py"
        ]
        print("运行管理员模块测试...")
    elif module == "shop_owner":
        test_files = [
            "test_shop_owner_base.py",
            "test_shop_owner_product.py",
            "test_shop_owner_order.py",
            "test_shop_owner_tag.py",
            "test_shop_owner_shop.py",
            "test_shop_owner_user.py"
        ]
        print("运行商家模块测试...")
    else:
        test_files = [
            "test_auth.py",
            "test_frontend.py",
            "test_admin_base.py",
            "test_admin_shop.py",
            "test_admin_product.py",
            "test_admin_user.py",
            "test_admin_order.py",
            "test_admin_tag.py",
            "test_admin_data.py",
            "test_shop_owner_base.py",
            "test_shop_owner_product.py",
            "test_shop_owner_order.py",
            "test_shop_owner_tag.py",
            "test_shop_owner_shop.py",
            "test_shop_owner_user.py"
        ]
        print("运行所有测试...")
    
    pytest_args = test_files
    if verbose:
        pytest_args.append("-v")
    
    exit_code = pytest.main(pytest_args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
