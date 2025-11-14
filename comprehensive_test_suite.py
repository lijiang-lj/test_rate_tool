# -*- coding: utf-8 -*-
"""
comprehensive_test_suite.py
工艺成本查询工具 - 全面测试套件

包含：
1. 基础功能测试样例
2. 边界条件测试样例  
3. 错误处理测试样例
4. 性能测试样例
5. 集成测试样例
"""

import os
import json
import time
import random
from typing import List, Dict, Any
from dotenv import load_dotenv
from process_rate_finder_tool import ProcessRateFinderTool


class ComprehensiveTestSuite:
    """工艺成本查询工具全面测试套件"""
    
    def __init__(self):
        # 加载环境变量
        BASE_DIR = os.path.dirname(__file__)
        env_path = os.path.join(BASE_DIR, ".env")
        load_dotenv(dotenv_path=env_path)
        
        # 设置代理
        proxy = os.getenv("PROXY_URL", "").strip()
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
            os.environ["ALL_PROXY"] = proxy
            os.environ["NO_PROXY"] = "localhost,127.0.0.1"
            print("✅ 强制全局代理启用")
        
        # 初始化工具
        self.tool = ProcessRateFinderTool()
        
        # 测试数据定义
        self.locations = ["Ningbo, Zhejiang", "Nanjing Chervon Auto Precision"]
        self.materials = ["AlSi9Mn", "AlSi9MnMoZr", "Al plate <6082>"]
        self.processes = [
            "Trimming", "KTL coating", "Melting", "Casting", "Deburring", 
            "Sand blasting", "Manual polishing", "Machining OP10", "Washing",
            "FSW", "Polishing", "Machining OP20", "Ultrasonic washing"
        ]
        self.units = ["CNY/h", "CNY/cm³", "CNY/kg"]
    
    def pretty_print_result(self, title: str, result_json: str, success: bool = True):
        """美化打印测试结果"""
        print("\n" + "=" * 80)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {title}")
        print("=" * 80)
        
        try:
            data = json.loads(result_json)
            print(f"▶ final_cost: {data.get('final_cost')} {data.get('final_unit')}")
            print(f"▶ base_hourly_cost (CNY/h): {data.get('base_hourly_cost')}")
            
            # 如果有错误信息，显示错误
            llm_result = data.get('llm_reasoning', {})
            if 'error' in llm_result:
                print(f"▶ Error: {llm_result.get('error')}")
            
            # CSV基准对比
            csv_baseline = data.get('csv_baseline', {})
            if csv_baseline:
                print(f"▶ CSV基准: {csv_baseline.get('low')}-{csv_baseline.get('high')} {csv_baseline.get('unit')}")
            
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            print("原始输出:", result_json[:500] + "..." if len(result_json) > 500 else result_json)
    
    def run_basic_functionality_tests(self) -> List[Dict[str, Any]]:
        """基础功能测试 - 覆盖所有计费单位和主要工艺"""
        print("\n" + "#" * 80)
        print("1. 基础功能测试")
        print("#" * 80)
        
        basic_test_cases = [
            # 按小时计费测试
            {
                "title": "基础测试 - Trimming工艺按小时计费",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 3110.0,
                "volume": 195.6,
                "annual_volume": 1_100_000,
                "unit": "CNY/h"
            },
            {
                "title": "基础测试 - Casting工艺按小时计费",
                "location": "Ningbo, Zhejiang",
                "process_name": "Casting",
                "material_name": "AlSi9Mn",
                "surface_area": 5000.0,
                "volume": 300.0,
                "annual_volume": 500_000,
                "unit": "CNY/h"
            },
            
            # 按体积计费测试
            {
                "title": "基础测试 - KTL coating工艺按体积计费",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 3110.0,
                "volume": 195.6,
                "annual_volume": 1_100_000,
                "unit": "CNY/cm³"
            },
            
            # 按重量计费测试
            {
                "title": "基础测试 - Melting工艺按重量计费",
                "location": "Ningbo, Zhejiang",
                "process_name": "Melting",
                "material_name": "AlSi9Mn",
                "surface_area": 3110.0,
                "volume": 195.6,
                "annual_volume": 1_100_000,
                "unit": "CNY/kg"
            },
            
            # 不同材料测试
            {
                "title": "基础测试 - AlSi9MnMoZr材料工艺",
                "location": "Nanjing Chervon Auto Precision",
                "process_name": "Trimming",
                "material_name": "AlSi9MnMoZr",
                "surface_area": 2500.0,
                "volume": 180.0,
                "annual_volume": 800_000,
                "unit": "CNY/h"
            }
        ]
        
        results = []
        for case in basic_test_cases:
            try:
                result = self.tool.run(**{k: v for k, v in case.items() if k != 'title'})
                self.pretty_print_result(case["title"], result, True)
                results.append({
                    "test_case": case["title"],
                    "success": True,
                    "result": json.loads(result)
                })
            except Exception as e:
                print(f"❌ {case['title']} 失败: {e}")
                results.append({
                    "test_case": case["title"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def run_boundary_condition_tests(self) -> List[Dict[str, Any]]:
        """边界条件测试 - 测试极端参数值"""
        print("\n" + "#" * 80)
        print("2. 边界条件测试")
        print("#" * 80)
        
        boundary_test_cases = [
            # 极小批量生产
            {
                "title": "边界测试 - 极小批量(100件)",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 100,
                "unit": "CNY/h"
            },
            # 极大批量生产
            {
                "title": "边界测试 - 极大批量(10M件)",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 10_000_000,
                "unit": "CNY/h"
            },
            # 极小体积
            {
                "title": "边界测试 - 极小体积(1cm³)",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 10.0,
                "volume": 1.0,
                "annual_volume": 50_000,
                "unit": "CNY/cm³"
            },
            # 极大体积
            {
                "title": "边界测试 - 极大体积(5000cm³)",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 10000.0,
                "volume": 5000.0,
                "annual_volume": 10_000,
                "unit": "CNY/cm³"
            },
            # 高表面积体积比
            {
                "title": "边界测试 - 高表面积体积比",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 5000.0,
                "volume": 50.0,
                "annual_volume": 100_000,
                "unit": "CNY/cm³"
            }
        ]
        
        results = []
        for case in boundary_test_cases:
            try:
                result = self.tool.run(**{k: v for k, v in case.items() if k != 'title'})
                self.pretty_print_result(case["title"], result, True)
                results.append({
                    "test_case": case["title"],
                    "success": True,
                    "result": json.loads(result)
                })
            except Exception as e:
                print(f"❌ {case['title']} 失败: {e}")
                results.append({
                    "test_case": case["title"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def run_error_handling_tests(self) -> List[Dict[str, Any]]:
        """错误处理测试 - 测试异常参数和边界情况"""
        print("\n" + "#" * 80)
        print("3. 错误处理测试")
        print("#" * 80)
        
        error_test_cases = [
            # 无效工艺名称
            {
                "title": "错误测试 - 无效工艺名称",
                "location": "Ningbo, Zhejiang",
                "process_name": "InvalidProcessXYZ",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 1000,
                "unit": "CNY/h",
                "expected_error": True
            },
            # 无效材料名称
            {
                "title": "错误测试 - 无效材料名称",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "InvalidMaterialXYZ",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 1000,
                "unit": "CNY/h",
                "expected_error": True
            },
            # 无效单位
            {
                "title": "错误测试 - 无效计费单位",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 1000,
                "unit": "CNY/invalid",
                "expected_error": True
            },
            # 零体积
            {
                "title": "错误测试 - 零体积",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 0.0,
                "annual_volume": 1000,
                "unit": "CNY/cm³",
                "expected_error": True
            },
            # 负值测试
            {
                "title": "错误测试 - 负年产量",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": -1000,
                "unit": "CNY/h",
                "expected_error": True
            }
        ]
        
        results = []
        for case in error_test_cases:
            try:
                result = self.tool.run(**{k: v for k, v in case.items() if k not in ['title', 'expected_error']})
                
                # 检查是否如预期产生了错误
                result_data = json.loads(result)
                llm_result = result_data.get('llm_reasoning', {})
                has_error = 'error' in llm_result or result_data.get('final_cost') is None
                
                success = has_error == case.get('expected_error', False)
                self.pretty_print_result(case["title"], result, success)
                
                results.append({
                    "test_case": case["title"],
                    "success": success,
                    "expected_error": case.get('expected_error', False),
                    "actual_has_error": has_error,
                    "result": result_data
                })
                
            except Exception as e:
                # 对于错误测试，异常可能是预期的
                expected_error = case.get('expected_error', False)
                success = expected_error
                print(f"{'✅' if success else '❌'} {case['title']}: {e}")
                results.append({
                    "test_case": case["title"],
                    "success": success,
                    "expected_error": expected_error,
                    "error": str(e)
                })
        
        return results
    
    def run_performance_tests(self) -> List[Dict[str, Any]]:
        """性能测试 - 测试查询时间和资源使用"""
        print("\n" + "#" * 80)
        print("4. 性能测试")
        print("#" * 80)
        
        performance_test_cases = [
            {
                "title": "性能测试 - 快速工艺查询",
                "location": "Ningbo, Zhejiang",
                "process_name": "Trimming",
                "material_name": "AlSi9Mn",
                "surface_area": 100.0,
                "volume": 10.0,
                "annual_volume": 1000,
                "unit": "CNY/h"
            },
            {
                "title": "性能测试 - 复杂工艺查询",
                "location": "Ningbo, Zhejiang",
                "process_name": "KTL coating",
                "material_name": "AlSi9Mn",
                "surface_area": 1000.0,
                "volume": 100.0,
                "annual_volume": 50000,
                "unit": "CNY/cm³"
            }
        ]
        
        results = []
        for case in performance_test_cases:
            try:
                start_time = time.time()
                result = self.tool.run(**{k: v for k, v in case.items() if k != 'title'})
                end_time = time.time()
                
                execution_time = end_time - start_time
                success = execution_time < 30.0  # 假设30秒内完成为成功
                
                print(f"\n⏱️ {case['title']}")
                print(f"执行时间: {execution_time:.2f}秒")
                print(f"状态: {'✅ 通过' if success else '❌ 超时'}")
                
                results.append({
                    "test_case": case["title"],
                    "success": success,
                    "execution_time": execution_time,
                    "result": json.loads(result)
                })
                
            except Exception as e:
                print(f"❌ {case['title']} 失败: {e}")
                results.append({
                    "test_case": case["title"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def run_integration_tests(self) -> List[Dict[str, Any]]:
        """集成测试 - 测试完整工作流程和多轮查询"""
        print("\n" + "#" * 80)
        print("5. 集成测试")
        print("#" * 80)
        
        # 多轮一致性测试 - 相同参数多次查询
        integration_test_cases = [
            {
                "title": "集成测试 - 多轮查询一致性",
                "test_cases": [
                    {
                        "location": "Ningbo, Zhejiang",
                        "process_name": "Trimming",
                        "material_name": "AlSi9Mn",
                        "surface_area": 100.0,
                        "volume": 10.0,
                        "annual_volume": 1000,
                        "unit": "CNY/h"
                    }
                ],
                "iterations": 3
            },
            {
                "title": "集成测试 - 多工艺批量查询",
                "test_cases": [
                    {
                        "location": "Ningbo, Zhejiang",
                        "process_name": "Trimming",
                        "material_name": "AlSi9Mn",
                        "surface_area": 100.0,
                        "volume": 10.0,
                        "annual_volume": 1000,
                        "unit": "CNY/h"
                    },
                    {
                        "location": "Ningbo, Zhejiang",
                        "process_name": "Deburring",
                        "material_name": "AlSi9Mn",
                        "surface_area": 100.0,
                        "volume": 10.0,
                        "annual_volume": 1000,
                        "unit": "CNY/h"
                    },
                    {
                        "location": "Ningbo, Zhejiang",
                        "process_name": "Sand blasting",
                        "material_name": "AlSi9Mn",
                        "surface_area": 100.0,
                        "volume": 10.0,
                        "annual_volume": 1000,
                        "unit": "CNY/h"
                    }
                ],
                "iterations": 1
            }
        ]
        
        results = []
        for integration_case in integration_test_cases:
            print(f"\n🔗 {integration_case['title']}")
            
            iteration_results = []
            for i in range(integration_case['iterations']):
                print(f"迭代 {i+1}/{integration_case['iterations']}")
                
                for case in integration_case['test_cases']:
                    try:
                        start_time = time.time()
                        result = self.tool.run(**case)
                        end_time = time.time()
                        
                        result_data = json.loads(result)
                        iteration_results.append({
                            "test_case": f"{integration_case['title']} - 迭代{i+1}",
                            "success": True,
                            "execution_time": end_time - start_time,
                            "result": result_data
                        })
                        
                        print(f"  ✅ {case['process_name']}: {result_data.get('final_cost')} {result_data.get('final_unit')}")
                        
                    except Exception as e:
                        print(f"  ❌ {case['process_name']} 失败: {e}")
                        iteration_results.append({
                            "test_case": f"{integration_case['title']} - 迭代{i+1}",
                            "success": False,
                            "error": str(e)
                        })
            
            results.extend(iteration_results)
        
        return results
    
    def generate_test_report(self, all_results: Dict[str, List[Dict[str, Any]]]):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📊 测试报告摘要")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            category_total = len(results)
            category_passed = sum(1 for r in results if r.get('success', False))
            
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"\n{category}:")
            print(f"  通过: {category_passed}/{category_total} ({category_passed/category_total*100:.1f}%)")
            
            # 显示失败的测试用例
            failed_cases = [r for r in results if not r.get('success', False)]
            for failed in failed_cases[:3]:  # 只显示前3个失败用例
                print(f"    ❌ {failed.get('test_case', 'Unknown')}")
                if 'error' in failed:
                    print(f"      错误: {failed['error'][:100]}...")
        
        print(f"\n📈 总体结果:")
        print(f"  总测试用例: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  失败: {total_tests - passed_tests}")
        print(f"  通过率: {passed_tests/total_tests*100:.1f}%")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行全面测试套件")
        print("=" * 80)
        
        start_time = time.time()
        
        all_results = {
            "基础功能测试": self.run_basic_functionality_tests(),
            "边界条件测试": self.run_boundary_condition_tests(),
            "错误处理测试": self.run_error_handling_tests(),
            "性能测试": self.run_performance_tests(),
            "集成测试": self.run_integration_tests()
        }
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 生成报告
        self.generate_test_report(all_results)
        
        print(f"\n⏱️ 总执行时间: {total_time:.2f}秒")
        print("🎉 测试套件执行完成！")


def main():
    """主函数 - 运行全面测试套件"""
    try:
        test_suite = ComprehensiveTestSuite()
        test_suite.run_all_tests()
    except Exception as e:
        print(f"❌ 测试套件初始化失败: {e}")
        print("请检查环境变量配置和依赖安装")


if __name__ == "__main__":
    main()
