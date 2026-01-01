import subprocess
import time
import json
import re
from datetime import datetime

def run_tests():
    """执行所有测试用例并记录执行时间和结果"""
    test_dir = r"d:\local_code_repo\OrderEase-Deploy\test"
    result_file = r"d:\local_code_repo\OrderEase-Deploy\test\test_results.json"
    
    # 测试模块列表
    test_modules = [
        ("admin", "管理员模块"),
        ("shop_owner", "商家模块"),
        ("auth", "认证模块"),
        ("frontend", "前端模块"),
    ]
    
    results = []
    all_test_cases = []
    
    print("=" * 80)
    print("开始执行所有测试用例")
    print("=" * 80)
    print("开始时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    for module_name, module_desc in test_modules:
        print("\n" + "=" * 40)
        print("执行 " + module_desc + " (" + module_name + ")")
        print("=" * 40)
        
        module_start_time = time.time()
        
        try:
            # 执行测试
            cmd = [
                "python", "-m", "pytest",
                module_name + "/",
                "--html=report.html",
                "--self-contained-html",
                "-v",  # 详细输出以获取每个测试用例的时间
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
            
            # 提取每个测试用例的结果
            test_case_pattern = r'([a-zA-Z0-9_]+::[a-zA-Z0-9_]+::test_[a-zA-Z0-9_]+)\s+(PASSED|FAILED)'
            test_cases = re.findall(test_case_pattern, output)
            
            # 解析每个测试用例的时间
            time_pattern = r'([a-zA-Z0-9_]+::[a-zA-Z0-9_]+::test_[a-zA-Z0-9_]+)\s+\[(\d+\.\d+)s\]'
            time_matches = re.findall(time_pattern, output)
            
            # 创建测试用例结果字典
            test_case_results = {}
            for test_case in test_cases:
                test_case_results[test_case[0]] = {
                    "status": test_case[1],
                    "time": None
                }
            
            # 为每个测试用例添加时间
            for time_match in time_matches:
                if len(time_match) >= 2:
                    test_case_name = time_match[0]
                    test_time = float(time_match[1])
                    if test_case_name in test_case_results:
                        test_case_results[test_case_name]["time"] = test_time
            
            # 统计通过和失败数量
            passed_count = output.count("PASSED")
            failed_count = output.count("FAILED")
            
            module_result = {
                "module": module_name,
                "description": module_desc,
                "start_time": datetime.fromtimestamp(module_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": datetime.fromtimestamp(module_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                "duration": round(module_duration, 2),
                "passed": passed_count,
                "failed": failed_count,
                "exit_code": result.returncode,
                "test_cases": test_case_results,
                "output": output[-2000:] if len(output) > 2000 else output  # 保留最后2000字符
            }
            
            results.append(module_result)
            
            print("完成 - 耗时: " + str(round(module_duration, 2)) + "秒")
            print("  通过: " + str(passed_count) + ", 失败: " + str(failed_count))
            
        except Exception as e:
            module_end_time = time.time()
            module_duration = module_end_time - module_start_time
            
            module_result = {
                "module": module_name,
                "description": module_desc,
                "start_time": datetime.fromtimestamp(module_start_time).strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": datetime.fromtimestamp(module_end_time).strftime('%Y-%m-%d %H:%M:%S'),
                "duration": round(module_duration, 2),
                "passed": 0,
                "failed": 0,
                "exit_code": -1,
                "error": str(e),
                "test_cases": {}
            }
            
            results.append(module_result)
            print("错误: " + str(e))
    
    # 计算总体统计
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_duration = sum(r["duration"] for r in results)
    
    # 收集所有测试用例
    for r in results:
        for test_case, test_result in r["test_cases"].items():
            all_test_cases.append({
                "module": r["module"],
                "test_case": test_case,
                "status": test_result["status"],
                "time": test_result["time"]
            })
    
    # 保存结果到JSON文件
    summary = {
        "test_run": {
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_duration": round(total_duration, 2)
        },
        "modules": results,
        "all_test_cases": all_test_cases,
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
    print("总通过: " + str(total_passed))
    print("总失败: " + str(total_failed))
    print("成功率: " + str(summary['summary']['success_rate']) + "%")
    print("\n详细结果已保存到: " + result_file)
    print("=" * 80)
    
    # 打印各模块详情
    print("\n各模块测试结果:")
    print("-" * 80)
    for r in results:
        status = "✓" if r["failed"] == 0 else "✗"
        print(status + " " + r['description'] + ": 通过=" + str(r['passed']) + ", 失败=" + str(r['failed']) + ", 耗时=" + str(r['duration']) + "s")
    print("-" * 80)
    
    # 打印最慢的10个测试用例
    sorted_test_cases = sorted(all_test_cases, key=lambda x: x["time"] or 0, reverse=True)
    print("\n最慢的10个测试用例:")
    print("-" * 80)
    for i, test_case in enumerate(sorted_test_cases[:10]):
        status = "✓" if test_case["status"] == "PASSED" else "✗"
        time_str = str(test_case["time"]) + "s" if test_case["time"] else "N/A"
        print(f"{i+1}. {test_case['module']}::{test_case['test_case']} - {status} - {time_str}")
    print("-" * 80)

if __name__ == "__main__":
    run_tests()