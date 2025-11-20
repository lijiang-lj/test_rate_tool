# 工艺成本智能 Agent

## 项目简介
该项目实现了一个工艺成本智能 Agent，提供对多种制造工艺的成本估算，支持对话式查询、参数推理和多轮上下文记忆。

## 功能特性
- 对话式查询：自然语言交互，无需记忆参数格式  
- 智能参数推理：自动补全和引导缺失参数  
- 多轮对话记忆：上下文记忆，实现连续查询  
- 格式化输出：清晰展示成本分解和推理过程  
- 多种计费单位：支持 CNY/h、CNY/cm³、CNY/kg  

## 目录
- [安装与环境配置](#安装与环境配置)  
- [运行方式](#运行方式)  
- [模块说明](#模块说明)  
- [示例](#示例)  
- [常见问题](#常见问题)  
- [许可协议](#许可协议)  

## 安装与环境配置
1. 克隆仓库
2. 激活已创建的 Conda 环境
```bash
conda activate test1
```
3. 创建并编辑 `.env`，参考：
```env
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
TAVILY_API_KEY=your-tavily-key
PROXY_URL=http://user:password@proxy.company.com:8080
```
4. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行方式
### 交互式对话
```bash
python interactive_agent.py
```
### 脚本测试
```bash
python process_cost_agent.py
```

## 模块说明
### azure_proxy.py
用于加载环境变量并启动 Flask HTTP 代理，转发 Cline 请求到 Azure OpenAI：  
点击查看 [azure_proxy.py](azure_proxy.py:1)

### interactive_agent.py
命令行交互入口，处理用户命令并调用 Agent：  
点击查看 [interactive_agent.py](interactive_agent.py:1)

### process_cost_agent.py
实现 `ProcessCostAgent`，封装 `AgentExecutor` 及工具列表，负责多轮对话、参数推理和输出格式化：  
点击查看 [process_cost_agent.py](process_cost_agent.py:1)

### process_rate_finder_tool.py
核心成本计算工具，根据用户输入调用 Tavily 搜索并计算工艺成本：  
点击查看 [process_rate_finder_tool.py](process_rate_finder_tool.py:1)

### 测试模块
包含单元和集成测试：  
- `comprehensive_test_suite.py`  
- 各类 `test_*.py`  

### MCP 服务
本地 GitHub MCP 服务，源代码位于 `mcp/github-server/src/index.ts`，用于文件和 PR 操作。

### 自动化脚本
脚本位于 `scripts/`，用于环境部署、测试和提交：  
- `setup_github_mcp.ps1`  
- `gh_commit.ps1`  
- `gh_test.ps1`  

## 示例
```python
from process_cost_agent import ProcessCostAgent

agent = ProcessCostAgent()
response = agent.chat("查询宁波 AlSi9Mn KTL coating 成本，表面积 3110 cm²，体积 195.6 cm³，年产 110 万件，按体积计费")
print(response)
```

## 常见问题
- 响应太慢？尝试降低 `temperature` 或使用更快模型。  
- 参数不完整？请提供完整数值，如“体积 200 cm³”。  

## 许可协议
MIT License