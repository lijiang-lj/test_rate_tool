# test_cline.py
# -*- coding: utf-8 -*-

"""
简单测试样例：
- 初始化 ProcessRateFinderTool
- 使用多组参数调用 .run(...)
- 打印返回的 JSON 结果，验证环境变量和代理设置
- 样例涵盖多种工艺和计费单位
"""

import os
from dotenv import load_dotenv
import json
from process_rate_finder_tool import ProcessRateFinderTool

# 加载 .env 文件
BASE_DIR = os.path.dirname(__file__)
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)
print(f"✅ 已加载 .env 文件: {env_path}")

# 配置全局代理，参考公司代理规范
proxy = os.getenv("PROXY_URL", "").strip()
if not proxy:
    # 示例默认公司代理（不能写明真实密码）
    proxy = "http://user:password@rb-proxy-company.com:8080"

if proxy:
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    os.environ["ALL_PROXY"] = proxy
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    print("✅ 全局代理已启用:", proxy)
else:
    print("⚠️ 未配置 PROXY_URL，使用直连")

def pretty_print(title: str, result_json: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    try:
        data = json.loads(result_json)
        print(f"▶ final_cost: {data.get('final_cost')} {data.get('final_unit')}")
        print(f"▶ base_hourly_cost (CNY/h): {data.get('base_hourly_cost')}")
        print("▶ csv_baseline:", data.get("csv_baseline"))
        print("\n🔍 Full JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print("❌ JSON 解析失败:", e)
        print("原始输出:", result_json)

def main():
    tool = ProcessRateFinderTool()

    test_cases = [
        {
            "title": "Test Case 1: Melting - CNY/kg",
            "kwargs": dict(
                location="Ningbo, Zhejiang",
                process_name="Melting",
                material_name="AlSi9Mn",
                surface_area=3110.0,
                volume=195.6,
                annual_volume=1_100_000,
                unit="CNY/kg",
            ),
        },
        {
            "title": "Test Case 2: Casting - CNY/h",
            "kwargs": dict(
                location="Shenzhen, Guangdong",
                process_name="Casting",
                material_name="AlSi10Mg",
                surface_area=2800.0,
                volume=150.0,
                annual_volume=800_000,
                unit="CNY/h",
            ),
        },
        {
            "title": "Test Case 3: Machining OP10 - CNY/pcs",
            "kwargs": dict(
                location="Shanghai",
                process_name="Machining OP10",
                material_name="Steel A36",
                surface_area=4500.0,
                volume=300.0,
                annual_volume=2_000_000,
                unit="CNY/pcs",
            ),
        },
        {
            "title": "Test Case 4: KTL coating - USD/cm³",
            "kwargs": dict(
                location="Guangzhou, Guangdong",
                process_name="KTL coating",
                material_name="Plastic ABS",
                surface_area=2600.0,
                volume=100.0,
                annual_volume=500_000,
                unit="USD/cm³",
            ),
        },
    ]

    for case in test_cases:
        print("\n" + "#" * 80)
        print(f"Running test: {case['title']}")
        print("#" * 80)
        try:
            result = tool.run(**case["kwargs"])
            pretty_print(case["title"], result)
        except Exception as e:
            print("❌ 测试调用失败:", e)


if __name__ == "__main__":
    main()
