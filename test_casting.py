# test_casting.py
# -*- coding: utf-8 -*-

"""
专门测试 Casting 工艺的成本估算（使用 1250t 东芝压铸机）

测试参数：
- 地区: Ningbo, Zhejiang
- 材料: AlSi9Mn
- 表面积: 3110.0 cm²
- 体积: 195.6 cm³
- 年产量: 800,000 件（80万）
- 目标单位: CNY/h
- 设备: 1250t 东芝压铸机（在 tool 内部自动识别）
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
    """美化打印结果"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    try:
        data = json.loads(result_json)

        # 提取关键信息
        query = data.get("query", {})
        final_cost = data.get("final_cost")
        final_unit = data.get("final_unit")
        base_hourly_cost = data.get("base_hourly_cost")
        csv_baseline = data.get("csv_baseline", {})
        llm_reasoning = data.get("llm_reasoning", {})

        print("\n📋 查询参数：")
        print(f"  - 地区: {query.get('location')}")
        print(f"  - 工艺: {query.get('process_name')}")
        print(f"  - 材料: {query.get('material_name')}")
        print(f"  - 表面积: {query.get('surface_area_cm2')} cm²")
        print(f"  - 体积: {query.get('volume_cm3')} cm³")
        print(f"  - 年产量: {query.get('annual_volume'):,} 件")
        print(f"  - 目标单位: {query.get('target_unit')}")

        print("\n💰 成本估算结果：")
        print(f"  ▶ 最终成本: {final_cost} {final_unit}")
        print(f"  ▶ 小时成本 (CNY/h): {base_hourly_cost}")

        print("\n📊 CSV 基准数据（对比参考）：")
        if csv_baseline:
            print(f"  - Low: {csv_baseline.get('low')}")
            print(f"  - High: {csv_baseline.get('high')}")
            print(f"  - Unit: {csv_baseline.get('unit')}")
            print(f"  - Source: {csv_baseline.get('source')}")
        else:
            print("  - 未找到匹配的 CSV 基准数据")

        print("\n🧠 LLM 推理详情：")
        base_cost = llm_reasoning.get("base_hourly_cost", {})
        if base_cost:
            print(f"  - 人工成本: {base_cost.get('labor_CNY_per_hour')} CNY/h")
            print(f"  - 能源成本: {base_cost.get('energy_CNY_per_hour')} CNY/h")
            print(f"  - 设备折旧: {base_cost.get('depreciation_CNY_per_hour')} CNY/h")
            print(f"  - 总成本: {base_cost.get('total_CNY_per_hour')} CNY/h")

        processing_speed = llm_reasoning.get("processing_speed", {})
        if processing_speed:
            print(f"\n⚙️ 加工速度估算：")
            print(f"  - 速度: {processing_speed.get('value')} {processing_speed.get('unit')}")

        unit_conv = llm_reasoning.get("unit_conversion", {})
        if unit_conv:
            print(f"\n🔄 单位转换：")
            print(f"  - 从: {unit_conv.get('from_unit')}")
            print(f"  - 到: {unit_conv.get('to_unit')}")
            print(f"  - 转换系数: {unit_conv.get('conversion_factor')}")

        print("\n🔍 完整 JSON 输出：")
        print(json.dumps(data, ensure_ascii=False, indent=2))

    except Exception as e:
        print("❌ JSON 解析失败：", e)
        print("原始输出：", result_json)


def main():
    print("\n" + "#" * 80)
    print("🏭 Casting 工艺成本估算测试")
    print("   设备：1250t 东芝压铸机")
    print("   年产量：800,000 件")
    print("#" * 80)

    # 初始化工具实例
    tool = ProcessRateFinderTool()

    # 测试参数
    test_params = {
        "location": "Ningbo, Zhejiang",
        "process_name": "Casting",
        "material_name": "AlSi9Mn",
        "surface_area": 3110.0,
        "volume": 195.6,
        "annual_volume": 800_000,  # 80万件
        "unit": "CNY/h",
    }

    print("\n开始执行测试...")
    print("调试: 即将调用 tool.run")
    try:
        print("调试: 调用 tool.run 开始")
        result = tool.run(**test_params)
        print("调试: tool.run 返回", result)
        pretty_print("Casting 工艺成本估算结果（1250t 东芝压铸机，年产量 80万件）", result)
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ 测试失败：", e)
        print("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
