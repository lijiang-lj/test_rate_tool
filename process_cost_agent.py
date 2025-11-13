# -*- coding: utf-8 -*-
"""
process_cost_agent.py — 工艺成本智能 Agent
功能：
1. 对话式成本查询
2. 自动补全缺失参数
3. 智能解析用户意图
4. 格式化输出结果
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
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
# 导入你的工具
from process_rate_finder_tool import ProcessRateFinderTool


class ProcessCostAgent:
    """工艺成本智能 Agent"""

    def __init__(self):
        """初始化 Agent"""
        # 1. 加载 .env 文件
        BASE_DIR = os.path.dirname(__file__)
        env_path = os.path.join(BASE_DIR, ".env")
        load_dotenv(dotenv_path=env_path)
        print(f"✅ 已加载 .env 文件: {env_path}")

        # 2. 配置代理（如果有 PROXY_URL）
        self._setup_proxy()

    def _setup_proxy(self):
        """配置全局代理"""
        proxy = os.getenv("PROXY_URL", "").strip()
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
            os.environ["ALL_PROXY"] = proxy
            os.environ["NO_PROXY"] = "localhost,127.0.0.1"
            print(f"✅ 已启用代理: {proxy}")
        else:
            print("⚠️ 未配置 PROXY_URL，将不使用代理")

        # 3. 初始化 Agent 组件
        self._initialize_agent()

    def _initialize_agent(self):
        """初始化 LLM、工具和 Agent"""
        print("🔄 正在初始化 Agent...")

        # 1. 初始化 LLM
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=1,
        )
        print("  ✓ Azure OpenAI 已连接")

        # 2. 初始化工具
        self.tool = ProcessRateFinderTool()
        self.tools = [self.tool.as_tool()]
        print("  ✓ 工具已加载")

        # 3. 创建 Agent Prompt
        self.prompt = self._create_prompt()

        # 4. 创建 Agent（使用 tool calling 而不是 function calling）
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        # 5. 创建 Executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )
        print("  ✓ Agent 创建完成")

        # 6. 对话历史
        self.chat_history = []
        print("✅ Agent 初始化成功！\n")

    def _create_prompt(self) -> ChatPromptTemplate:
        """创建 Agent 的系统提示词"""
        system_template = """
你是一位专业的制造业成本工程师助手，精通工艺成本估算。

你的能力：
- 使用 process_rate_finder 工具查询工艺成本
- 支持三种计费单位：CNY/h（按小时）、CNY/cm³（按体积）、CNY/kg（按重量）
- 自动推理缺失的参数（如表面积、体积等）
- 提供详细的成本分析和建议

参数说明：
1. location: 生产地区（如 "Ningbo, Zhejiang"）
2. process_name: 工艺名称（如 "Melting", "Casting", "Machining OP10" 等）
3. material_name: 材料名称（如 "AlSi9Mn"）
4. surface_area: 表面积（cm²）
5. volume: 体积（cm³）
6. annual_volume: 年产量（件）
7. unit: 计费单位（CNY/h, CNY/cm³, CNY/kg）

工作流程：
1. 理解用户意图，识别关键信息
2. 如果缺少必要参数，向用户询问或基于常识推理
3. 调用 process_rate_finder 工具
4. 解析结果，用清晰的格式展示给用户
5. 提供成本分析和优化建议

注意事项：
- 如果用户只提供部分信息，你需要智能补全或询问
- 对于几何参数（表面积、体积），可以基于典型零件尺寸估算
- 年产量会影响设备折旧分摊，需要准确获取
- 输出结果要清晰、专业、易懂

示例对话：
用户: "帮我算一下宁波的压铸成本"
你: "好的，我需要一些额外信息：
    1. 材料是什么？（如 AlSi9Mn）
    2. 零件的大概尺寸？（或提供表面积和体积）
    3. 年产量是多少？
    4. 希望按什么单位计费？（小时/体积/重量）"

用户: "材料是 AlSi9Mn，年产 110 万件，按小时计费"
你: [调用工具] → "根据查询结果，宁波地区 AlSi9Mn 压铸工艺成本为..."
"""

        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def chat(self, user_input: str) -> str:
        """
        与 Agent 对话

        Args:
            user_input: 用户输入

        Returns:
            Agent 回复
        """
        print("\n" + "=" * 80)
        print(f"👤 用户: {user_input}")
        print("=" * 80)

        try:
            # 调用 Agent
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history,
            })

            # 提取输出
            output = response.get("output", "抱歉，我无法处理您的请求。")

            # 更新对话历史
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=output))

            print("\n" + "=" * 80)
            print(f"🤖 Agent: {output}")
            print("=" * 80 + "\n")

            return output

        except Exception as e:
            error_msg = f"❌ Agent 执行失败: {str(e)}"
            print(error_msg)
            return error_msg

    def reset(self):
        """重置对话历史"""
        self.chat_history = []
        print("✅ 对话历史已重置")

    def format_cost_result(self, result_json: str) -> str:
        """
        格式化工具返回的 JSON 结果

        Args:
            result_json: process_rate_finder 返回的 JSON 字符串

        Returns:
            格式化后的文本
        """
        try:
            data = json.loads(result_json)

            # 提取关键信息
            query = data.get("query", {})
            final_cost = data.get("final_cost")
            final_unit = data.get("final_unit")
            base_hourly = data.get("base_hourly_cost")
            csv_baseline = data.get("csv_baseline", {})
            llm_reasoning = data.get("llm_reasoning", {})

            # 构建输出
            output = []
            output.append("📊 成本查询结果")
            output.append("-" * 60)

            # 查询参数
            output.append("\n🔍 查询参数:")
            output.append(f"  • 地区: {query.get('location')}")
            output.append(f"  • 工艺: {query.get('process_name')}")
            output.append(f"  • 材料: {query.get('material_name')}")
            output.append(f"  • 表面积: {query.get('surface_area_cm2')} cm²")
            output.append(f"  • 体积: {query.get('volume_cm3')} cm³")
            output.append(f"  • 年产量: {query.get('annual_volume'):,} 件")

            # 成本结果
            output.append("\n💰 成本估算:")
            if final_cost is not None:
                output.append(f"  • 最终成本: {final_cost:.2f} {final_unit}")
            if base_hourly is not None:
                output.append(f"  • 基础小时成本: {base_hourly:.2f} CNY/h")

            # 成本分解
            if "base_hourly_cost" in llm_reasoning:
                breakdown = llm_reasoning["base_hourly_cost"]
                output.append("\n📋 成本分解 (CNY/h):")
                output.append(f"  • 人工: {breakdown.get('labor_CNY_per_hour', 0):.2f}")
                output.append(f"  • 能源: {breakdown.get('energy_CNY_per_hour', 0):.2f}")
                output.append(f"  • 设备折旧: {breakdown.get('depreciation_CNY_per_hour', 0):.2f}")

            # CSV 基准对比
            if csv_baseline:
                output.append("\n📚 CSV 基准数据:")
                low = csv_baseline.get("low")
                high = csv_baseline.get("high")
                if low and high:
                    output.append(f"  • 参考区间: {low:.2f} - {high:.2f} {csv_baseline.get('unit')}")
                else:
                    output.append("  • 无匹配数据")

            # 推理过程
            if "detailed_reasoning" in llm_reasoning:
                output.append("\n🧠 推理过程:")
                reasoning = llm_reasoning["detailed_reasoning"]
                # 截取前 200 字符
                output.append(f"  {reasoning[:200]}...")

            return "\n".join(output)

        except Exception as e:
            return f"❌ 结果解析失败: {str(e)}\n原始数据: {result_json}"


def main():
    """测试 Agent"""

    print("\n" + "🤖" * 40)
    print("欢迎使用工艺成本智能 Agent！")
    print("🤖" * 40 + "\n")

    # 初始化 Agent
    agent = ProcessCostAgent()

    # 测试对话场景
    test_scenarios = [
        # 场景 1: 完整信息查询
        {
            "name": "场景1: 完整参数查询",
            "messages": [
                "帮我查询宁波地区 AlSi9Mn 材料的 Trimming 工艺成本，表面积 3110 cm²，体积 195.6 cm³，年产量 110 万件，按小时计费"
            ]
        },

        # 场景 2: 缺少参数，需要 Agent 询问
        {
            "name": "场景2: 缺少参数",
            "messages": [
                "帮我算一下宁波的 Melting 工艺成本",
                "材料是 AlSi9Mn，年产量 110 万件，体积 195.6 cm³，按重量计费"
            ]
        },

        # 场景 3: 多工序查询
        {
            "name": "场景3: 多工序对比",
            "messages": [
                "对比一下 Casting 和 Machining OP10 这两个工艺的成本，都在宁波，材料 AlSi9Mn，年产 110 万件，表面积 3110 cm²，体积 195.6 cm³，按小时计费"
            ]
        },
    ]

    # 执行测试场景
    for scenario in test_scenarios:
        print("\n" + "🎬" * 40)
        print(f"开始测试: {scenario['name']}")
        print("🎬" * 40 + "\n")

        for msg in scenario["messages"]:
            response = agent.chat(msg)

        # 重置对话历史
        agent.reset()
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()
