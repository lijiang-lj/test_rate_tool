# -*- coding: utf-8 -*-
"""
process_rate_finder_tool.py — v2.1 (完全由LLM推理，无硬编码公式)
功能：通过 Tavily 查询实时价格，由 Azure OpenAI 的 LLM 根据 metallurgical knowledge 自动推理工艺成本。
"""

import os
import json
import re
from typing import Dict, Any

import pandas as pd
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_tavily import TavilySearch

load_dotenv()


class ProcessRateFinderArgs(BaseModel):
    """工艺成本查询参数"""
    location: str = Field(..., description="生产地区")
    process_name: str = Field(..., description="工艺名称")
    material_name: str = Field(..., description="材料名称")
    surface_area: float = Field(..., description="表面积 cm²")
    volume: float = Field(..., description="体积 cm³")
    annual_volume: int = Field(..., description="年产量（件）")
    unit: str = Field(
        ...,
        description="成本单位：CNY/h（按小时）, CNY/cm³（按体积）, CNY/kg（按重量）"
    )


class ProcessRateFinderTool:
    """工艺成本查询工具 - 完全由 LLM 推理，无硬编码公式"""

    def __init__(self, llm: AzureChatOpenAI | None = None, csv_path: str | None = None) -> None:
        self.name = "process_rate_finder"
        self.description = (
            "通过 Tavily 查询实时价格数据，由 GPT-4/5 基于 metallurgical knowledge "
            "自动推理工艺成本（人工 + 能源 + 设备折旧），支持输出 CNY/h, CNY/cm³, CNY/kg"
        )

        # LLM：从环境变量读取 Azure OpenAI 配置
        self.llm = llm or AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=1.0,
        )

        # Tavily API key
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        # CSV 基准数据（仅用于结果对比，不参与数值计算）
        self.csv_path = csv_path or os.path.join(
            os.path.dirname(__file__),
            "data",
            "process_rates.csv",
        )
        self.base_data = self._load_csv_data()

    # --------------------------------------------------------------------- #
    # CSV 相关
    # --------------------------------------------------------------------- #
    def _load_csv_data(self) -> pd.DataFrame:
        """加载 CSV 基准数据（仅用于对比）"""
        try:
            df = pd.read_csv(self.csv_path, encoding="utf-8-sig")
            print(f"[INFO] ✅ 成功加载 CSV 数据：{len(df)} 行")
            return df
        except Exception as e:
            print(f"[WARN] ⚠️ CSV 加载失败：{e}")
            return pd.DataFrame()

    def _query_csv_baseline(
        self,
        location: str,
        process_name: str,
        material_name: str,
    ) -> Dict[str, Any]:
        """从 CSV 查询基准数据（仅用于对比，不参与计算）"""
        if self.base_data.empty:
            return {}

        df = self.base_data

        filtered = df[
            df["Location"].str.contains(location, case=False, na=False)
            & df["sub_process step"].str.contains(process_name, case=False, na=False)
            & df["material_name"].str.contains(material_name, case=False, na=False)
        ]

        if filtered.empty:
            print(f"[WARN] CSV 中未找到匹配：{location} | {process_name} | {material_name}")
            return {}

        row = filtered.iloc[0]
        return {
            "low": float(row.get("Low", 0)) if pd.notna(row.get("Low")) else None,
            "high": float(row.get("High", 0)) if pd.notna(row.get("High")) else None,
            "unit": row.get("Unit", "/h"),
            "source": "CSV基准数据",
        }

    # --------------------------------------------------------------------- #
    # Tavily 搜索
    # --------------------------------------------------------------------- #
    def _tavily_search(self, query: str) -> str:
        """Tavily 搜索封装

        使用 langchain_tavily.TavilySearch 工具。
        为了兼容不同版本的返回类型，这里做了两层处理：
        - 如果结果对象有 .content 属性（例如 ToolMessage），返回其 content
        - 否则直接把结果转成字符串返回
        """
        if not self.tavily_key:
            print("[WARN] Tavily API key 未配置，跳过在线查询")
            return ""

        try:
            search = TavilySearch(api_key=self.tavily_key, max_results=5)
            print(f"🔍 Tavily 查询: {query}")
            result = search.invoke(query)

            # ToolMessage / AIMessage 等
            if hasattr(result, "content"):
                return str(result.content or "")

            # 其他类型（str / dict 等），一律转成字符串
            return "" if result is None else str(result)
        except Exception as e:
            # 不做任何数值“兜底”，只记录日志并返回空字符串
            print(f"[WARN] Tavily 查询失败: {e}")
            return ""

    # --------------------------------------------------------------------- #
    # 实时数据收集
    # --------------------------------------------------------------------- #
    def _gather_realtime_data(self, location: str, process_name: str) -> Dict[str, str]:
        """收集所有实时数据（人工、能源、设备、工艺信息）"""
        print("\n[INFO] 📡 开始收集实时数据...")

        # 1. 查询人工成本
        labor_query = f"China {location} manufacturing labor cost per hour 2025 CNY"
        labor_data = self._tavily_search(labor_query)

        # 2. 查询能源价格
        energy_query = (
            f"China {location} industrial electricity water natural gas price 2025"
        )
        energy_data = self._tavily_search(energy_query)

        # 3. 查询工艺设备信息
        equipment_query = (
            f"{process_name} process equipment cost depreciation manufacturing"
        )
        equipment_data = self._tavily_search(equipment_query)

        # 4. 查询工艺能耗信息
        consumption_query = (
            f"{process_name} process energy consumption electricity water gas"
        )
        consumption_data = self._tavily_search(consumption_query)

        print("[INFO] ✅ 实时数据收集完成\n")

        return {
            "labor_data": labor_data or "未查询到人工成本数据",
            "energy_data": energy_data or "未查询到能源价格数据",
            "equipment_data": equipment_data or "未查询到设备信息",
            "consumption_data": consumption_data or "未查询到工艺能耗数据",
        }

    # --------------------------------------------------------------------- #
    # LLM 推理
    # --------------------------------------------------------------------- #
    def _llm_cost_reasoning(
        self,
        location: str,
        process_name: str,
        material_name: str,
        surface_area: float,
        volume: float,
        annual_volume: int,
        unit: str,
        realtime_data: Dict[str, str],
    ) -> Dict[str, Any]:
        """让 LLM 基于实时数据推理工艺成本"""

        prompt_template = ChatPromptTemplate.from_template(
            """
你是一位资深的制造业成本工程师，精通 metallurgical processes 和 cost estimation。

你的任务：
1. 结合实时数据（人工、能源、设备折旧、工艺能耗）和专业知识，估算 {process_name} 工艺的成本。
2. 支持三种计费方式：CNY/h（按小时）、CNY/cm³（按体积）、CNY/kg（按重量）。
3. 必须严格输出 JSON，不能有 markdown 包裹。

-------------------------
【工艺参数】
- 地区：{location}
- 工艺：{process_name}
- 材料：{material_name}
- 表面积：{surface_area} cm²
- 体积：{volume} cm³
- 年产量：{annual_volume} 件
- 目标计费单位：{unit}

【实时数据（原始文本，仅供你理解和提取数值）】
- 人工成本数据：
{labor_data}

- 能源价格数据：
{energy_data}

- 设备成本 / 折旧数据：
{equipment_data}

- 工艺能耗数据：
{consumption_data}

-------------------------
【推理要求】

1. 先从实时数据中提取你认为可靠的数值（例如人工单价、电价、气价、典型能耗等），并在 reasoning 中说明来源。
2. 建立一个合理的 cost model，将成本拆解为：
   - labor（人工）
   - energy（能源）
   - depreciation（设备折旧）
3. 先在 CNY/h 维度上给出 total_cost_CNY_per_hour，然后再根据目标单位 {unit} 做单位转换：
   - CNY/cm³：需要估算单位时间内可加工体积（cm³/h）
   - CNY/kg：需要估算材料密度（g/cm³）并计算单件重量（kg），再估算件数/小时
4. 所有假设必须在 reasoning 中说清楚，比如：
   - 如果缺少某项数据，可以基于中国制造业的典型区间给出一个合理区间，并说明是假设。
   - 不允许直接拍脑袋给出完全无依据的数值。
5. 请务必保证最终 JSON 可以被 Python json.loads 正确解析。

-------------------------
【输出 JSON 模板（示例结构）】

请严格按以下结构输出（字段可以根据需要扩展，但不要删除已有字段）：

{{
  "target_unit": "{unit}",
  "material_density_g_per_cm3": <如果需要按 CNY/kg，则给出估算的材料密度，否则可以为 null>,
  "calculated_weight_kg": <如果需要按 CNY/kg，则给出单件估算重量，否则可以为 null>,
  "processing_speed": {{
    "value": <数值>,
    "unit": "<例如 cm³/h 或 kg/h 或 pcs/h>",
    "reasoning": "<你是如何估算加工速度的>"
  }},
  "base_hourly_cost": {{
    "labor_CNY_per_hour": <数值>,
    "energy_CNY_per_hour": <数值>,
    "depreciation_CNY_per_hour": <数值>,
    "total_CNY_per_hour": <数值>,
    "reasoning": "<成本拆分的详细推理过程>"
  }},
  "unit_conversion": {{
    "from_unit": "CNY/h",
    "to_unit": "{unit}",
    "conversion_factor": <数值>,
    "reasoning": "<单位转换的推理过程>"
  }},
  "final_cost": <数值>,
  "final_unit": "{unit}",
  "cost_breakdown": {{
    "labor": <数值>,
    "energy": <数值>,
    "depreciation": <数值>
  }},
  "detailed_reasoning": "<完整推理过程，包括所有关键假设和中间步骤>"
}}

注意：
- 所有推理必须基于提供的实时数据和 metallurgical knowledge。
- 如果某项数据缺失，请在 reasoning 中清楚说明假设值及其合理区间。
- 必须输出纯 JSON，不要有 ```json``` 或 ``` 包裹。
- 单位转换必须合理且有依据。
"""
        )

        print("[INFO] 🧠 LLM 开始推理成本...")

        try:
            chain = prompt_template | self.llm
            response = chain.invoke(
                {
                    "location": location,
                    "process_name": process_name,
                    "material_name": material_name,
                    "surface_area": surface_area,
                    "volume": volume,
                    "annual_volume": annual_volume,
                    "unit": unit,
                    **realtime_data,
                }
            )

            # 一些模型会自动加 ```json``` 包裹，这里统一清理
            content = response.content.strip()
            content = re.sub(r"```json\s*", "", content)
            content = re.sub(r"```\s*", "", content)
            content = content.strip()

            # 解析 JSON
            result = json.loads(content)
            print("[INFO] ✅ LLM 推理完成\n")
            return result

        except Exception as e:
            print(f"[ERROR] ❌ LLM 推理失败: {e}")
            # 不做数值“兜底”，只返回错误信息，方便上层处理
            return {
                "error": f"LLM推理失败: {str(e)}",
                "final_cost": None,
                "final_unit": unit,
                "base_hourly_cost": {},
            }

    # --------------------------------------------------------------------- #
    # 对外主入口
    # --------------------------------------------------------------------- #
    def run(
        self,
        location: str,
        process_name: str,
        material_name: str,
        surface_area: float,
        volume: float,
        annual_volume: int,
        unit: str,
    ) -> str:
        """主执行函数：负责串联 CSV 对比、实时数据和 LLM 推理"""

        print("\n" + "=" * 80)
        print("🚀 工艺成本查询 - 完全由 LLM 推理")
        print("=" * 80)
        print(f"📍 地区: {location}")
        print(f"🔧 工艺: {process_name}")
        print(f"🧱 材料: {material_name}")
        print(f"📐 表面积: {surface_area} cm²")
        print(f"📊 体积: {volume} cm³")
        print(f"📦 年产量: {annual_volume:,} 件")
        print(f"💰 目标单位: {unit}")
        print("=" * 80 + "\n")

        # 1. CSV 基准（仅用于对比）
        csv_baseline = self._query_csv_baseline(location, process_name, material_name)

        # 2. 实时数据
        realtime_data = self._gather_realtime_data(location, process_name)

        # 3. LLM 推理成本
        llm_result = self._llm_cost_reasoning(
            location=location,
            process_name=process_name,
            material_name=material_name,
            surface_area=surface_area,
            volume=volume,
            annual_volume=annual_volume,
            unit=unit,
            realtime_data=realtime_data,
        )

        # 4. 统一输出结构
        output: Dict[str, Any] = {
            "query": {
                "location": location,
                "process_name": process_name,
                "material_name": material_name,
                "surface_area_cm2": surface_area,
                "volume_cm3": volume,
                "annual_volume": annual_volume,
                "target_unit": unit,
            },
            "csv_baseline": csv_baseline,
            "llm_reasoning": llm_result,
            "final_cost": llm_result.get("final_cost"),
            "final_unit": llm_result.get("final_unit", unit),
            "base_hourly_cost": (
                llm_result.get("base_hourly_cost", {}) or {}
            ).get("total_CNY_per_hour"),
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    def as_tool(self) -> StructuredTool:
        """将当前类暴露为 LangChain 的 StructuredTool"""
        return StructuredTool.from_function(
            func=self.run,
            name=self.name,
            description=self.description,
            args_schema=ProcessRateFinderArgs,
        )


if __name__ == "__main__":
    tool = ProcessRateFinderTool()

    # 示例 1：按小时计费
    print("\n" + "=" * 80)
    print("示例1：Trimming 工艺 - 按小时计费（CNY/h）")
    print("=" * 80)
    result = tool.run(
        location="Ningbo, Zhejiang",
        process_name="Trimming",
        material_name="AlSi9Mn",
        surface_area=3110.0,
        volume=195.6,
        annual_volume=1_100_000,
        unit="CNY/h",
    )
    print("\n📊 结果：")
    print(result)

    # 示例 2：按体积计费
    print("\n\n" + "=" * 80)
    print("示例2：KTL coating 工艺 - 按体积计费（CNY/cm³）")
    print("=" * 80)
    result = tool.run(
        location="Ningbo, Zhejiang",
        process_name="KTL coating",
        material_name="AlSi9Mn",
        surface_area=3110.0,
        volume=195.6,
        annual_volume=1_100_000,
        unit="CNY/cm³",
    )
    print("\n📊 结果：")
    print(result)

    # 示例 3：按重量计费
    print("\n\n" + "=" * 80)
    print("示例3：Melting 工艺 - 按重量计费（CNY/kg）")
    print("=" * 80)
    result = tool.run(
        location="Ningbo, Zhejiang",
        process_name="Melting",
        material_name="AlSi9Mn",
        surface_area=3110.0,
        volume=195.6,
        annual_volume=1_100_000,
        unit="CNY/kg",
    )
    print("\n📊 结果：")
    print(result)
