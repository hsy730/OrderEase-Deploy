import subprocess
import time
import json
from datetime import datetime

def run_business_flow_tests():
    """优先执行业务流程测试，然后执行其他测试"""
    test_dir = r"d:\local_code_repo\OrderEase-Deploy\test"
    result_file = r"d:\local_code_repo\OrderEase-Deploy\test\business_flow_test_results.json"
    
    print("=" * 80)
    print("开始执行业务流程测试")
    print("=" * 80)
    print("开始时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 第一步：执行业务流程测试
    print("\n" + "=" * 40)
    print("执行业务流程测试")
    print("=" * 40)
    
    business_flow_start_time = time.time()
    
    try:
        # 执行业务流程测试
        cmd = [
            "python", "-m", "pytest",
            "admin/test_business_flow.py",
            "--html=business_flow_report.html",
            "--self-contained-html",
            "-v",  # 详细输出
            "--tb=short"  # 简短的错误信息
        ]
        
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'  # 忽略编码错误
        )
        
        business_flow_end_time = time.time()
        business_flow_duration = business_flow_end_time - business_flow_start_time
        
        # 解析测试结果
        output = result.stdout + result.stderr
        passed_count = output.count("PASSED")
        failed_count = output.count("FAILED")
        
        business_flow_result = {
            "module": "business_flow",
            "description": "业务流程测试",
            "start_time": datetime.fromtimestamp(business_flow_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(business_flow_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "duration": round(business_flow_duration, 2),
            "passed": passed_count,
            "failed": failed_count,
            "exit_code": result.returncode,
            "output": output[-2000:] if len(output) > 2000 else output  # 保留最后2000字符
        }
        
        print("完成 - 耗时: " + str(round(business_flow_duration, 2)) + "秒")
        print("  通过: " + str(passed_count) + ", 失败: " + str(failed_count))
        
        # 如果业务流程测试失败，可以选择是否继续执行其他测试
        if failed_count > 0:
            print("\n警告：业务流程测试存在失败，可能会影响其他测试结果")
            # 可以在这里添加逻辑，决定是否继续执行其他测试
            
    except Exception as e:
        business_flow_end_time = time.time()
        business_flow_duration = business_flow_end_time - business_flow_start_time
        
        business_flow_result = {
            "module": "business_flow",
            "description": "业务流程测试",
            "start_time": datetime.fromtimestamp(business_flow_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(business_flow_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "duration": round(business_flow_duration, 2),
            "passed": 0,
            "failed": 0,
            "exit_code": -1,
            "error": str(e)
        }
        
        print("错误: " + str(e))
    
    # 第二步：执行其他测试（跳过被标记的测试）
    print("\n" + "=" * 40)
    print("执行其他测试（跳过已整合的业务测试）")
    print("=" * 40)
    
    other_tests_start_time = time.time()
    
    # 测试模块列表（排除已整合的业务测试）
    test_modules = [
        ("admin/test_user.py", "管理员用户模块"),
        ("admin/test_tag.py", "管理员标签模块"),
        ("shop_owner", "商家模块"),
        ("auth", "认证模块"),
        ("frontend", "前端模块"),
    ]
    
    other_results = []
    
    for module_path, module_desc in test_modules:
        print("\n执行 " + module_desc + " (" + module_path + ")")
        
        module_start_time = time.time()
        
        try:
            # 执行测试
            cmd = [
                "python", "-m", "pytest",
                module_path,
                "-v",  # 详细输出
                "--tb=short"  # 简短的错误信息
            ]
            
            result = subprocess.run(
                cmd,
                cwd=test_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'  # 忽略编码错误
            )
            
            module_end_time = time.time()
            module_duration = module_end_time - module_start_time
            
            # 解析测试结果
            output = result.stdout + result.stderr
            passed_count = output.count("PASSED")
            failed_count = output.count("FAILED")
            
            module_result = {
                "module": module_path,
                "description": module_desc,
                "start_time": datetime.fromtimestamp(module_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": datetime.fromtimestamp(module_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                "duration": round(module_duration, 2),
                "passed": passed_count,
                "failed": failed_count,
                "exit_code": result.returncode,
                "output": output[-2000:] if len(output) > 2000 else output  # 保留最后2000字符
            }
            
            other_results.append(module_result)
            
            print("完成 - 耗时: " + str(round(module_duration, 2)) + "秒")
            print("  通过: " + str(passed_count) + ", 失败: " + str(failed_count))
            
        except Exception as e:
            module_end_time = time.time()
            module_duration = module_end_time - module_start_time
            
            module_result = {
                "module": module_path,
                "description": module_desc,
                "start_time": datetime.fromtimestamp(module_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": datetime.fromtimestamp(module_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                "duration": round(module_duration, 2),
                "passed": 0,
                "failed": 0,
                "exit_code": -1,
                "error": str(e)
            }
            
            other_results.append(module_result)
            print("错误: " + str(e))
    
    other_tests_end_time = time.time()
    other_tests_duration = other_tests_end_time - other_tests_start_time
    
    # 计算总体统计
    total_passed = business_flow_result["passed"] + sum(r["passed"] for r in other_results)
    total_failed = business_flow_result["failed"] + sum(r["failed"] for r in other_results)
    total_duration = business_flow_result["duration"] + other_tests_duration
    
    # 保存结果到JSON文件
    summary = {
        "test_run": {
            "start_time": datetime.fromtimestamp(business_flow_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(other_tests_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "total_duration": round(total_duration, 2)
        },
        "business_flow": business_flow_result,
        "other_tests": other_results,
        "summary": {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_tests": total_passed + total_failed,
            "success_rate": round((total_passed / (total_passed + total_failed)) * 100, 2) if (total_passed + total_failed) > 0 else 0
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试执行完成")
    print("=" * 80)
    print("结束时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("总耗时: " + str(round(total_duration, 2)) + "秒")
    print("业务流程测试: 通过=" + str(business_flow_result["passed"]) + ", 失败=" + str(business_flow_result["failed"]))
    print("其他测试: 通过=" + str(sum(r["passed"] for r in other_results)) + ", 失败=" + str(sum(r["failed"] for r in other_results)))
    print("总通过: " + str(total_passed))
    print("总失败: " + str(total_failed))
    print("成功率: " + str(summary['summary']['success_rate']) + "%")
    print("\n详细结果已保存到: " + result_file)
    print("=" * 80)
    
    # 打印各模块详情
    print("\n各模块测试结果:")
    print("-" * 80)
    status = "✓" if business_flow_result["failed"] == 0 else "✗"
    print(status + " " + business_flow_result['description'] + ": 通过=" + str(business_flow_result['passed']) + ", 失败=" + str(business_flow_result['failed']) + ", 耗时=" + str(business_flow_result['duration']) + "s")
    
    for r in other_results:
        status = "✓" if r["failed"] == 0 else "✗"
        print(status + " " + r['description'] + ": 通过=" + str(r['passed']) + ", 失败=" + str(r['failed']) + ", 耗时=" + str(r['duration']) + "s")
    print("-" * 80)

if __name__ == "__main__":
    run_business_flow_tests()