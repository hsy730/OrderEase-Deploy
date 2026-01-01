import subprocess
import time
import json
from datetime import datetime
import os

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
            # 创建临时JSON报告文件
            json_report_file = os.path.join(test_dir, f"{module_name}_report.json")
            
            # 执行测试
            cmd = [
                "python", "-m", "pytest",
                module_name + "/",
                "--json-report",
                f"--json-report-file={json_report_file}",
                "--html=report.html",
                "--self-contained-html",
                "--tb=short",
                "--durations=0",
                "-v"
            ]
            
            print(f"命令: {' '.join(cmd)}")
            
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
            
            # 解析JSON报告
            test_case_results = {}
            passed_count = 0
            failed_count = 0
            
            try:
                with open(json_report_file, 'r', encoding='utf-8') as f:
                    json_report = json.load(f)
                    
                # 提取测试用例信息
                for test in json_report.get('tests', []):
                    test_name = test.get('nodeid', '')
                    test_status = test.get('outcome', '')
                    test_duration = test.get('duration', 0)
                    
                    # 提取类名和方法名
                    if '::' in test_name:
                        parts = test_name.split('::')
                        if len(parts) >= 3:
                            class_name = parts[1]
                            method_name = parts[2]
                            test_case_name = f"{class_name}::{method_name}"
                        else:
                            test_case_name = test_name
                    else:
                        test_case_name = test_name
                    
                    test_case_results[test_case_name] = {
                        "status": test_status.upper(),
                        "time": test_duration
                    }
                    
                    if test_status.upper() == "PASSED":
                        passed_count += 1
                    elif test_status.upper() == "FAILED":
                        failed_count += 1
                        
            except Exception as e:
                print(f"解析JSON报告失败: {e}")
                # 如果JSON解析失败，从输出中提取基本统计
                output = result.stdout + result.stderr
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
                "test_cases": test_case_results
            }
            
            results.append(module_result)
            
            print("完成 - 耗时: " + str(round(module_duration, 2)) + "秒")
            print("  通过: " + str(passed_count) + ", 失败: " + str(failed_count))
            
            # 清理临时JSON报告文件
            try:
                os.remove(json_report_file)
            except:
                pass
            
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
                "time": test_result["time"],
                "start_time": r["start_time"],
                "end_time": r["end_time"]
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
    if all_test_cases:
        sorted_test_cases = sorted(all_test_cases, key=lambda x: x["time"] or 0, reverse=True)
        print("\n最慢的10个测试用例:")
        print("-" * 80)
        for i, test_case in enumerate(sorted_test_cases[:10]):
            status = "✓" if test_case["status"] == "PASSED" else "✗"
            time_str = f"{test_case['time']:.3f}s" if test_case["time"] else "N/A"
            print(f"{i+1}. {test_case['module']}::{test_case['test_case']} - {status} - {time_str}")
        print("-" * 80)

if __name__ == "__main__":
    run_tests()