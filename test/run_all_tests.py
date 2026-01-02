import subprocess
import sys
import os

def run_tests():
    """执行所有测试，优先运行业务流程测试"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 80)
    print("开始执行所有测试（优先运行业务流程测试）")
    print("=" * 80)
    
    # 优先运行业务流程测试
    print("\n正在执行业务流程测试...")
    business_flow_script = os.path.join(test_dir, "run_business_flow_tests.py")
    
    try:
        result = subprocess.run(
            [sys.executable, business_flow_script],
            cwd=test_dir,
            text=True
        )
        
        if result.returncode != 0:
            print("警告：业务流程测试执行失败，但继续执行其他测试")
    except Exception as e:
        print(f"执行业务流程测试时出错: {e}")
        print("继续执行其他测试...")
    
    print("\n" + "=" * 80)
    print("所有测试执行完成")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()