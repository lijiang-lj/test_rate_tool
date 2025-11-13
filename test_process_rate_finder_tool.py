# test_process_rate_finder_tool.py
# -*- coding: utf-8 -*-

"""
简单烟雾测试：
- 直接调用 ProcessRateFinderTool.run(...)
- 打印返回的 JSON 结果
- 主要验证：环境变量、Tavily、Azure OpenAI 配置是否正常
"""

import os
from dotenv import load_dotenv

# 1) 加载 .env
BASE_DIR = os.path.dirname(__file__)
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)
print(f"✅ 已加载 .env 文件: {env_path}")

# 2) 读取 PROXY_URL 并设置为全局代理（和 test_agent.py 一致的风格）
proxy = os.getenv("PROXY_URL", "").strip()

# 如果你想像 test_agent.py 一样给一个默认值，可以这样：
if not proxy:
    # 用你们自己的默认公司代理，下面只是示意（别把真实密码写死在仓库里）
    proxy = "http://user:password@rb-proxy-company.com:8080"

if proxy:
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    os.environ["ALL_PROXY"] = proxy
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    print("✅ 强制全局代理启用:", proxy)
else:
    print("⚠️ 未配置 PROXY_URL，走直连！")

# 3) ⚠️ 一定要在设置完代理之后再导入你的 tool
import json
from process_rate_finder_tool import ProcessRateFinderTool  # 原来的 import 保留

def pretty_print(title: str, result_json: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    try:
        data = json.loads(result_json)
        # 只打印关键信息，避免太长
        print(f"▶ final_cost: {data.get('final_cost')} {data.get('final_unit')}")
        print(f"▶ base_hourly_cost (CNY/h): {data.get('base_hourly_cost')}")
        print("▶ csv_baseline:", data.get("csv_baseline"))
        print("\n🔍 full JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print("❌ JSON 解析失败：", e)
        print("原始输出：", result_json)


def main():
    # 初始化工具（会自动从 .env 里读 Azure / Tavily 的 key）
    tool = ProcessRateFinderTool()

    # 用三组典型参数测试（基本沿用你文件里的示例）
    test_cases = [
        {
            "title": "Case 1：Trimming 工艺 - 按小时计费 (CNY/h)",
            "kwargs": dict(
                location="Ningbo, Zhejiang",
                process_name="Trimming",
                material_name="AlSi9Mn",
                surface_area=3110.0,
                volume=195.6,
                annual_volume=1_100_000,
                unit="CNY/h",
            ),
        },
        {
            "title": "Case 2：KTL coating 工艺 - 按体积计费 (CNY/cm³)",
            "kwargs": dict(
                location="Ningbo, Zhejiang",
                process_name="KTL coating",
                material_name="AlSi9Mn",
                surface_area=3110.0,
                volume=195.6,
                annual_volume=1_100_000,
                unit="CNY/cm³",
            ),
        },
        {
            "title": "Case 3：Melting 工艺 - 按重量计费 (CNY/kg)",
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
    ]

    for case in test_cases:
        print("\n" + "#" * 80)
        print("开始测试：", case["title"])
        print("#" * 80)

        try:
            result = tool.run(**case["kwargs"])
            pretty_print(case["title"], result)
        except Exception as e:
            print("❌ 调用失败：", e)


if __name__ == "__main__":
    main()
