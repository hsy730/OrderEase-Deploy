#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行所有测试用例并记录每个测试用例的开始和结束时间
使用JUnit XML格式获取更准确的测试时间
"""

import subprocess
import json
import os
import time
from datetime import datetime
import sys
import xml.etree.ElementTree as ET

def run_tests_with_junit_timing():
    """运行所有测试并使用JUnit XML记录详细的测试用例时间信息"""
    
    # 测试模块配置
    test_modules = [
        {
            "file": "admin/test_base.py",
            "name": "admin",
            "description": "管理员模块"
        },
        {
            "file": "admin/test_shop.py",
            "name": "admin_shop",
            "description": "管理员-店铺模块"
        },
        {
            "file": "admin/test_user.py",
            "name": "admin_user",
            "description": "管理员-用户模块"
        },
        {
            "file": "admin/test_product.py",
            "name": "admin_product",
            "description": "管理员-商品模块"
        },
        {
            "file": "admin/test_order.py",
            "name": "admin_order",
            "description": "管理员-订单模块"
        },
        {
            "file": "shop_owner/test_base.py",
            "name": "shop_owner",
            "description": "店铺所有者模块"
        },
        {
            "file": "shop_owner/test_product.py",
            "name": "shop_owner_product",
            "description": "店铺所有者-商品模块"
        },
        {
            "file": "shop_owner/test_order.py",
            "name": "shop_owner_order",
            "description": "店铺所有者-订单模块"
        },
        {
            "file": "frontend/test_product.py",
            "name": "frontend_product",
            "description": "前端用户-商品模块"
        },
        {
            "file": "frontend/test_order.py",
            "name": "frontend_order",
            "description": "前端用户-订单模块"
        }
    ]
    
    # 结果存储
    results = {
        "test_run": {
            "start_time": "",
            "end_time": "",
            "total_duration": 0
        },
        "modules": []
    }
    
    # 记录整体开始时间
    test_run_start = datetime.now()
    results["test_run"]["start_time"] = test_run_start.strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 80)
    print("开始执行所有测试模块")
    print(f"开始时间: {results['test_run']['start_time']}")
    print("=" * 80)
    
    # 逐个运行测试模块
    for module in test_modules:
        if not os.path.exists(module["file"]):
            print(f"\n警告: 测试文件 {module['file']} 不存在，跳过此模块")
            continue
            
        module_start_time = datetime.now()
        
        module_info = {
            "module": module["name"],
            "description": module["description"],
            "start_time": module_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_cases": {}
        }
        
        print(f"\n{'='*60}")
        print(f"正在运行模块: {module['description']} ({module['file']})")
        print(f"开始时间: {module_info['start_time']}")
        print(f"{'='*60}")
        
        # JUnit XML文件路径
        junit_file = f"junit_{module['name']}.xml"
        
        # 运行pytest生成JUnit XML报告
        cmd = [
            "pytest", 
            module["file"], 
            "-v",
            "--tb=short",
            "--junit-xml", junit_file
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        module_end_time = datetime.now()
        module_info["end_time"] = module_end_time.strftime("%Y-%m-%d %H:%M:%S")
        module_info["duration"] = (module_end_time - module_start_time).total_seconds()
        
        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = 0
        failed = 0
        
        # 查找包含测试结果的行
        for line in output_lines:
            # 匹配类似 "7 passed, 30 failed" 的行
            if " passed" in line and " failed" in line:
                import re
                # 使用正则表达式提取数字
                passed_match = re.search(r'(\d+)\s+passed', line)
                failed_match = re.search(r'(\d+)\s+failed', line)
                
                if passed_match:
                    passed = int(passed_match.group(1))
                if failed_match:
                    failed = int(failed_match.group(1))
            # 匹配类似 "7 passed in 20.08s" 的行
            elif " passed in " in line:
                import re
                passed_match = re.search(r'(\d+)\s+passed', line)
                if passed_match:
                    passed = int(passed_match.group(1))
                failed = 0
            # 匹配类似 "30 failed in 20.08s" 的行
            elif " failed in " in line:
                import re
                failed_match = re.search(r'(\d+)\s+failed', line)
                if failed_match:
                    failed = int(failed_match.group(1))
                passed = 0
        
        module_info["passed"] = passed
        module_info["failed"] = failed
        module_info["exit_code"] = result.returncode
        
        # 解析JUnit XML文件获取测试用例时间
        if os.path.exists(junit_file):
            try:
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                # 遍历所有testsuite
                for testsuite in root.findall('testsuite'):
                    # 获取测试套件的时间戳
                    suite_timestamp = testsuite.get('timestamp', '')
                    if suite_timestamp:
                        try:
                            # 解析ISO格式时间戳
                            suite_start_time = datetime.fromisoformat(suite_timestamp.replace('Z', '+00:00'))
                            suite_start_time = suite_start_time.timestamp()
                        except:
                            suite_start_time = module_start_time.timestamp()
                    else:
                        suite_start_time = module_start_time.timestamp()
                    
                    # 遍历所有测试用例
                    current_time = suite_start_time
                    for testcase in testsuite.findall('testcase'):
                        test_name = testcase.get('name', '')
                        class_name = testcase.get('classname', '')
                        full_name = f"{class_name}::{test_name}" if class_name else test_name
                        
                        # 获取测试用例时间
                        duration = float(testcase.get('time', 0))
                        
                        # 计算开始和结束时间
                        test_start_time = current_time
                        test_end_time = current_time + duration
                        current_time += duration  # 更新当前时间为下一个测试的开始时间
                        
                        # 检查测试状态
                        status = "PASSED"
                        if testcase.find('failure') is not None:
                            status = "FAILED"
                        elif testcase.find('error') is not None:
                            status = "ERROR"
                        elif testcase.find('skipped') is not None:
                            status = "SKIPPED"
                        
                        module_info["test_cases"][full_name] = {
                            "status": status,
                            "duration": duration,
                            "start_time": datetime.fromtimestamp(test_start_time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                            "end_time": datetime.fromtimestamp(test_end_time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        }
                
                # 清理XML文件
                os.remove(junit_file)
                
            except Exception as e:
                print(f"解析JUnit XML文件失败: {e}")
                module_info["test_cases"] = {}
        else:
            print(f"警告: JUnit XML文件 {junit_file} 未生成")
            module_info["test_cases"] = {}
        
        # 打印模块测试结果摘要
        print(f"\n模块测试完成:")
        print(f"  通过: {module_info['passed']}")
        print(f"  失败: {module_info['failed']}")
        print(f"  耗时: {module_info['duration']:.2f}秒")
        print(f"  结束时间: {module_info['end_time']}")
        print(f"  测试用例数: {len(module_info['test_cases'])}")
        
        # 如果有失败的测试，打印部分输出
        if result.returncode != 0:
            print("\n部分错误输出:")
            error_lines = result.stderr.split('\n')
            for line in error_lines[:10]:  # 只显示前10行错误
                if line.strip():
                    print(f"  {line}")
            if len(error_lines) > 10:
                print(f"  ... (还有 {len(error_lines) - 10} 行错误输出)")
        
        results["modules"].append(module_info)
    
    # 记录整体结束时间
    test_run_end = datetime.now()
    results["test_run"]["end_time"] = test_run_end.strftime("%Y-%m-%d %H:%M:%S")
    results["test_run"]["total_duration"] = (test_run_end - test_run_start).total_seconds()
    
    # 保存结果到JSON文件
    with open("test_results_with_junit_times.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印总结
    print("\n" + "=" * 80)
    print("所有测试模块执行完成")
    print(f"总开始时间: {results['test_run']['start_time']}")
    print(f"总结束时间: {results['test_run']['end_time']}")
    print(f"总耗时: {results['test_run']['total_duration']:.2f}秒")
    
    total_passed = sum(m.get("passed", 0) for m in results["modules"])
    total_failed = sum(m.get("failed", 0) for m in results["modules"])
    total_test_cases = sum(len(m.get("test_cases", {})) for m in results["modules"])
    
    print(f"总通过数: {total_passed}")
    print(f"总失败数: {total_failed}")
    print(f"总测试用例数: {total_test_cases}")
    print(f"详细结果已保存到: test_results_with_junit_times.json")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    run_tests_with_junit_timing()