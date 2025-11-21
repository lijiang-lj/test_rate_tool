# -*- coding: utf-8 -*-
"""
process_rate_finder_tool.py — v2.3（加入 KTL / Casting 提示词增强版，仍然不硬编码计算公式）
功能：通过 Tavily 查询实时价格，由 Azure OpenAI 的 LLM 自动推理工艺成本。
特点：
- 内部统一用 CNY/h 做“基准成本维度”
- 目标单位 unit 完全由调用方传入，不在代码里硬编码任何枚举或 if-else
- 单位转换全部交给 LLM 在 prompt 里基于专业知识推理
- 对 KTL coating / Casting 仅在提示词层给出“拆分结构”和“给出网址”的要求，不写死任何数值
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
    location: str = Field(..., description="生产地区，例如：Ningbo, Zhejiang")
    process_name: str = Field(..., description="工艺名称，例如：Melting, Casting, Machining OP10 等")
    material_name: str = Field(..., description="材料名称，例如：AlSi9Mn")
    surface_area: float = Field(..., description="表面积，单位：cm²")
    volume: float = Field(..., description="体积，单位：cm³")
    annual_volume: int = Field(..., description="年产量（件/年）")
    unit: str = Field(
        ...,
        description=(
            "目标成本单位（完全自由字符串，不做枚举限制）。"
            "例如：CNY/h, CNY/cm³, CNY/kg, CNY/pcs, EUR/h, USD/kg 等。"
        ),
    )


class ProcessRateFinderTool:
    """工艺成本查询工具 - 完全由 LLM 推理，单位逻辑不在代码中硬编码"""

    def __init__(self, llm: AzureChatOpenAI | None = None, csv_path: str | None = None) -> None:
        self.name = "process_rate_finder"
        self.description = (
            "通过 Tavily 查询实时价格数据，由 GPT 模型基于 metallurgical knowledge "
            "自动推理工艺成本（人工 + 能源 + 设备折旧），"
            "内部统一在 CNY/h 维度上建模，再转换到调用方指定的任意目标单位。"
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

        # CSV 基准数据（仅用于结果对比）
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
            "unit": row.get("Unit", "UNKNOWN"),
            "source": "CSV基准数据",
        }

    # --------------------------------------------------------------------- #
    # Tavily 搜索
    # --------------------------------------------------------------------- #
    def _tavily_search(self, query: str) -> str:
        """Tavily 搜索封装（不做任何数值“兜底”，只返回原始文本）"""
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

            # 其他类型（str / dict 等）
            return "" if result is None else str(result)
        except Exception as e:
            print(f"[WARN] Tavily 查询失败: {e}")
            return ""

    # --------------------------------------------------------------------- #
    # 实时数据收集
    # --------------------------------------------------------------------- #
    def _gather_realtime_data(self, location: str, process_name: str) -> Dict[str, str]:
        """收集所有实时数据（人工、能源、设备、工艺信息）"""
        print("\n[INFO] 📡 开始收集实时数据...")

        labor_query = f"China {location} manufacturing labor cost per hour 2025 CNY"
        energy_query = f"China {location} industrial electricity water natural gas price 2025"
        equipment_query = f"{process_name} process equipment cost depreciation manufacturing"
        consumption_query = f"{process_name} process energy consumption electricity water gas"

        labor_data = self._tavily_search(labor_query)
        energy_data = self._tavily_search(energy_query)
        equipment_data = self._tavily_search(equipment_query)
        consumption_data = self._tavily_search(consumption_query)

        print("[INFO] ✅ 实时数据收集完成\n")

        return {
            "labor_data": labor_data or "未查询到人工成本数据",
            "energy_data": energy_data or "未查询到能源价格数据",
            "equipment_data": equipment_data or "未查询到设备信息",
            "consumption_data": consumption_data or "未查询到工艺能耗数据",
        }

    # --------------------------------------------------------------------- #
    # LLM 推理（单位逻辑统一从 prompt 层处理）
    # --------------------------------------------------------------------- #
    def _llm_cost_reasoning(
        self,
        location: str,
        process_name: str,
        material_name: str,
        surface_area: float,
        volume: float,
        annual_volume: int,
        target_unit: str,
        realtime_data: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        让 LLM 基于实时数据推理工艺成本：
        - 内部始终先在 CNY/h 维度拆成本（labor / energy / depreciation）
        - 然后再根据 target_unit 做单位转换
        - target_unit 可以是任何字符串，LLM 需要自己判断如何从 CNY/h 转到目标单位
        """

        prompt_template = ChatPromptTemplate.from_template(
            """
你是一位资深的制造业成本工程师，精通 metallurgical processes 和 cost estimation。

你的任务：
1. 结合实时数据（人工、能源、设备折旧、工艺能耗）和专业知识，估算 {process_name} 工艺的成本。
2. 内部请统一先在 CNY/h 维度上建模和拆分成本（labor + energy + depreciation）。
3. 然后将 CNY/h 转换为用户指定的最终计费单位："{target_unit}"。
   - 这个单位是完全自由字符串，可能是 CNY/h, CNY/cm³, CNY/kg, CNY/pcs, EUR/h, USD/kg, CNY/m² 等。
   - 你需要根据这个单位的含义，推理出合理的转换方式。
   - 如果目标单位与 CNY/h 无法直接通过物理量（体积、质量、表面积、件数、时间等）转换，请在 reasoning 中说明你的假设并给出一个清晰的转换逻辑。
4. 所有推理必须有物理和经济上的合理性，不能凭空拍脑袋。

-------------------------
【工艺参数】
- 地区：{location}
- 工艺：{process_name}
- 材料：{material_name}
- 表面积：{surface_area} cm²
- 体积：{volume} cm³
- 年产量：{annual_volume} 件/年
- 目标计费单位（完全自由字符串）：{target_unit}

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
【语言要求】
- 所有 reasoning 字段（包括 processing_speed.reasoning、base_hourly_cost.reasoning、
  unit_conversion.reasoning、detailed_reasoning）必须全部使用中文撰写。
- JSON 的字段名保持英文（如 processing_speed、final_cost），但所有描述性文字必须输出中文。
-------------------------

-------------------------
【推理与单位转换要求】

1. 先在 CNY/h 维度上建立 cost model，将成本拆解为：
   - labor_CNY_per_hour
   - energy_CNY_per_hour
   - depreciation_CNY_per_hour
   - total_CNY_per_hour

2. 如果工艺名称包含 "KTL"（例如 "KTL coating"），请参考典型 KTL 产线在实际商务 Workshop 中的拆分结构来构建成本模型（但不要照搬任何具体项目的数值，只学习结构和思路），可包括但不限于：
   - 管理与间接人工：
     - 如 workshop manager、shift leader、assistant、quality controller 等。
     - 用“人数 × RMB/小时 × 小时/天 / 产量（housing/天）”的方式先折算到单件，再统一折算到 CNY/h。
   - 直接操作工人工：
     - 根据操作工人数、工资水平（RMB/小时）、每天工作小时数和产量，计算每件人工成本，并统一到 CNY/h。
   - 设备折旧（KTL 线投资）：
     - 基于整条 KTL 线的投资金额，采用长期折旧思路（例如按 10 年、每年工作天数、每天工作小时数等逻辑）；
     - 不把折旧只摊在单一客户项目上，而是考虑多项目、多年的综合利用。
   - 厂房/空间成本：
     - 参考“面积 m² × RMB/m² / 月或天 / 产量”这种结构；
     - 注意如果只部分时间给某个客户生产，应按实际利用时间分摊，而不是 100% 全部摊给该客户。
   - 能源成本：
     - 以总功率 kW、利用率（0~1）、每日运行小时数以及当地电价（RMB/kWh）为基础；
     - 必要时可补充压缩空气、天然气、水处理等能耗成本。
   - 维护与治具成本：
     - 如 racks、plastic caps、passivation line、water treatment 等；
     - 以“每月/每天维护或更换费用 / 产量”的结构折算到每件，再统一折算到 CNY/h。
   - 质量检测与实验成本：
     - 如盐雾试验、清洁测试、水测试、拉拔测试等；
     - 将年度或每日测试费用按频次和产量分摊到单件，再统一到 CNY/h。
   - 其他间接费用 / RMOC / Overhead：
     - 在“直接成本小计”基础上施加合理的百分比（例如管理附加、风险附加等），
     - 但必须在 reasoning 中写清楚采用的百分比区间与依据，仅作为假设。
   - Scrap 报废成本：
     - 采用合理的 Scrap Rate（%）区间；
     - 将 Scrap 视为“合格件成本 × Scrap Rate”的附加成本。
   在 detailed_reasoning 中，请像商务 Workshop 一样，清晰列出各项假设（人数、工时、功率、面积、Scrap 率等）和每一项的计算逻辑，最终仍需汇总为 CNY/h 维度的 base_hourly_cost。

3. 如果工艺与高压压铸 / Die casting / HPDC 相关（例如 process_name 包含 "Casting"），请在设备折旧部分显式考虑压铸机投资，并遵守以下要求：
   - 你可以通过实时数据搜索，获取类似“1250t Toshiba die casting machine / 东芝 1250t 压铸机”的市场公开报价或投资金额，用于估算折旧成本。
   - 当你在推理中实际采用了某个公开网页上的设备价格（尤其是 1250t 东芝压铸机的价格）时：
     - 必须在 detailed_reasoning 或 base_hourly_cost.reasoning 文本中，写出你引用该价格的公开网页 URL，
       例如增加一行 `"source_url": "https://......"` 或 类似 “设备价格参考来源：https://......” 的说明。
     - URL 必须是真实可访问的网页地址，而不是随意编造的字符串。
     - 同时注明“该价格仅为公开市场参考价，用于折旧估算，并非合同价或最终报价”。
   - 如果在线搜索没有获得可靠或明确的设备报价网页：
     - 请在 detailed_reasoning 中明确写出“未找到可靠的 1250t 东芝压铸机公开报价 URL”的情况；
     - 根据同吨位压铸机的一般价格区间或行业常识，给出一个合理的假设投资金额；
     - 解释你假设的依据（例如行业报告、类似机型价格区间），但不要伪造 URL。
   - 压铸机折旧思路仍应采用长期折旧 + 产能分摊（例如按年工作小时数、利用率、小时产能等），
     避免把设备投资只摊在单一项目的总量上。

4. 完成上述工艺成本建模（包括 KTL 或 Casting 等特殊要求，如果适用）后，再根据 {target_unit} 的含义，设计一个合理的单位转换逻辑，例如：
   - 如果 {target_unit} 是 "CNY/cm³"：
     - 说明你如何估算单位时间内可加工体积（cm³/h），并将 CNY/h 换算为 CNY/cm³。
   - 如果 {target_unit} 是 "CNY/kg"：
     - 估算材料密度（g/cm³），计算单件重量（kg），推理单位时间可加工质量（kg/h），再完成转换。
   - 如果 {target_unit} 是 "CNY/pcs"：
     - 估算单位时间内可加工件数（pcs/h），从而转换为 CNY/pcs。
   - 如果 {target_unit} 是其它自定义单位（例如货币不同、包含多个物理量）：
     - 在 reasoning 中清楚解释你是如何从 CNY/h 映射到该单位的，并确保逻辑自洽。

5. 如果缺少某项数据，可以根据中国或全球制造业的典型区间给出一个合理区间，并在 reasoning 中明确标注为“假设”。

6. 最终输出必须是 **纯 JSON**，不能包含任何 markdown 语法或 ```json 包裹。

-------------------------
【输出 JSON 模板（示例结构）】

请严格按以下结构输出（字段可以根据需要扩展，但不要删除已有字段）：

{{
  "target_unit": "{target_unit}",
  "material_density_g_per_cm3": <如果需要按质量相关单位，则给出估算的材料密度，否则可以为 null>,
  "calculated_weight_kg": <如果需要按质量相关单位，则给出单件估算重量，否则可以为 null>,
  "processing_speed": {{
    "value": <数值>,
    "unit": "<例如 cm³/h 或 kg/h 或 pcs/h 等>",
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
    "to_unit": "{target_unit}",
    "conversion_factor": <数值>,
    "reasoning": "<单位转换的推理过程，尤其是如何从 CNY/h 得到目标单位的>"
  }},
  "final_cost": <数值>,
  "final_unit": "{target_unit}",
  "cost_breakdown": {{
    "labor": <数值>,
    "energy": <数值>,
    "depreciation": <数值>
  }},
  "detailed_reasoning": "<完整推理过程，包括所有关键假设和中间步骤>"
}}

注意：
- 你可以根据目标单位自由设计转换逻辑，但必须保证物理和经济上合理。
- 如果目标单位过于奇怪或信息不足，无法给出可靠转换，请在 detailed_reasoning 里解释局限性。
- 必须输出纯 JSON，不能有 ```json 或 ``` 包裹。
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
                    "target_unit": target_unit,
                    **realtime_data,
                }
            )

            content = response.content.strip()
            # 防止 LLM 用 ```json 包裹
            content = re.sub(r"```json\s*", "", content)
            content = re.sub(r"```\s*", "", content)
            content = content.strip()

            result = json.loads(content)
            print("[INFO] ✅ LLM 推理完成\n")
            return result

        except Exception as e:
            print(f"[ERROR] ❌ LLM 推理失败: {e}")
            return {
                "error": f"LLM推理失败: {str(e)}",
                "final_cost": None,
                "final_unit": target_unit,
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
        print(f"💰 目标单位: {unit}（自由字符串，无硬编码枚举）")
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
            target_unit=unit,
            realtime_data=realtime_data,
        )

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

    # 示例调用：你可以随便改不同单位，看 LLM 如何处理
    for process_name, unit in [
        ("Melting", "CNY/kg"),
        ("Casting", "CNY/h"),
        ("Machining OP10", "CNY/pcs"),
        ("KTL coating", "CNY/cm³"),
        ("Machining OP30", "USD/h"),
    ]:
        print("\n" + "=" * 80)
        print(f"示例：{process_name} - 目标单位：{unit}")
        print("=" * 80)
        result = tool.run(
            location="Ningbo, Zhejiang",
            process_name=process_name,
            material_name="AlSi9Mn",
            surface_area=3110.0,
            volume=195.6,
            annual_volume=1_100_000,
            unit=unit,
        )
        print("\n📊 结果：")
        print(result)
