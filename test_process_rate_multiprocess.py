# test_process_rate_multiprocess.py
# -*- coding: utf-8 -*-

"""
批量测试多个工序的成本估算：
- Melting（CNY/kg）
- Casting（CNY/h）
- Machining OP10（CNY/h）
- Machining OP20（CNY/h）
- Before KTL visual inspection & deburring（CNY/h）
- Machining OP30（CNY/h）

公共参数：
- 地区: Ningbo, Zhejiang
- 材料: AlSi9Mn
- 表面积: 3110.0 cm²
- 体积: 195.6 cm³
- 年产量: 1,100,000 件
"""

import os
import json
from dotenv import load_dotenv

# --------------------------------------------------------------------------------------
# 1. 加载 .env 并配置公司代理（如果有 PROXY_URL）
# --------------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)
print(f"✅ 已加载 .env 文件: {env_path}")

proxy = os.getenv("PROXY_URL", "").strip()
if proxy:
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    os.environ["ALL_PROXY"] = proxy
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    print("✅ 已启用代理:", proxy)
else:
    print("⚠️ 未配置 PROXY_URL，将不使用代理")

# --------------------------------------------------------------------------------------
# 2. 导入你的工具
# --------------------------------------------------------------------------------------
from process_rate_finder_tool import ProcessRateFinderTool


def pretty_print(title: str, result_json: str):
    """简单美化打印结果"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    try:
        data = json.loads(result_json)

        final_cost = data.get("final_cost")
        final_unit = data.get("final_unit")
        base_hourly_cost = data.get("base_hourly_cost")
        csv_baseline = data.get("csv_baseline")

        print(f"▶ final_cost: {final_cost} {final_unit}")
        print(f"▶ base_hourly_cost (CNY/h): {base_hourly_cost}")
        print(f"▶ csv_baseline: {csv_baseline}")

        print("\n🔍 full JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print("❌ JSON 解析失败：", e)
        print("原始输出：", result_json)


def main():
    # 初始化工具实例（内部会读取 Azure OpenAI 和 Tavily 的配置）
    tool = ProcessRateFinderTool()

    # 公共参数
    common_kwargs = dict(
        location="Ningbo, Zhejiang",
        material_name="AlSi9Mn",
        surface_area=3110.0,
        volume=195.6,
        annual_volume=1_100_000,
    )

    # 6 个待测工序
    test_cases = [
        # {
        #     "title": "Case 1：Melting 工艺 - 按重量计费 (CNY/kg)",
        #     "kwargs": dict(
        #         process_name="Melting",
        #         unit="CNY/kg",
        #         **common_kwargs,
        #     ),
        # },
        # {
        #     "title": "Case 2：Casting 工艺 - 按小时计费 (CNY/h)",
        #     "kwargs": dict(
        #         process_name="Casting",
        #         unit="CNY/h",
        #         **common_kwargs,
        #     ),
        # },
        {
            "title": "Case 3：Machining OP10 工艺 - 按小时计费 (CNY/h)",
            "kwargs": dict(
                process_name="Machining OP10",
                unit="CNY/h",
                **common_kwargs,
            ),
        },
        # {
        #     "title": "Case 4：Machining OP20 工艺 - 按小时计费 (CNY/h)",
        #     "kwargs": dict(
        #         process_name="Machining OP20",
        #         unit="CNY/h",
        #         **common_kwargs,
        #     ),
        # },
        {
            "title": "Case 5：KTL coating 工艺 - 按体积计费 (CNY/cm²)",
            "kwargs": dict(
                process_name=" KTL coating",
                unit="CNY/cm²",
                **common_kwargs,
            ),
        },
        # {
        #     "title": "Case 6：Machining OP30 工艺 - 按小时计费 (CNY/h)",
        #     "kwargs": dict(
        #         process_name="Machining OP30",
        #         unit="CNY/h",
        #         **common_kwargs,
        #     ),
        # },
        
    ]

    # 逐个执行
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
