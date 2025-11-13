# -*- coding: utf-8 -*-
"""
interactive_agent.py — 交互式工艺成本 Agent 测试
功能：命令行交互式对话，实时测试 Agent 能力
"""



import os
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

from process_cost_agent import ProcessCostAgent


def print_help():
    """打印帮助信息"""
    print("\n" + "=" * 80)
    print("📚 命令说明")
    print("=" * 80)
    print("  help    - 显示此帮助信息")
    print("  reset   - 重置对话历史")
    print("  quit    - 退出程序")
    print("  exit    - 退出程序")
    print("\n💡 示例问题:")
    print("  • 帮我查询宁波的 Trimming 工艺成本")
    print("  • 对比 Casting 和 Melting 两个工艺的成本")
    print("  • 宁波 AlSi9Mn 材料的 KTL coating 成本，年产 110 万件，按体积计费")
    print("=" * 80 + "\n")


def main():
    """主函数：交互式对话循环"""

    # 欢迎信息
    print("\n" + "🤖" * 40)
    print("欢迎使用工艺成本智能 Agent！")
    print("🤖" * 40)
    print("\n输入 'help' 查看命令说明，输入 'quit' 退出\n")

    # 初始化 Agent
    print("🔄 正在初始化 Agent...")
    try:
        agent = ProcessCostAgent()
        print("✅ Agent 初始化成功！\n")
    except Exception as e:
        print(f"❌ Agent 初始化失败: {e}")
        return

    # 对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("👤 你: ").strip()

            # 处理命令
            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 再见！感谢使用！\n")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if user_input.lower() == "reset":
                agent.reset()
                continue

            # 调用 Agent
            response = agent.chat(user_input)

        except KeyboardInterrupt:
            print("\n\n👋 再见！感谢使用！\n")
            break

        except Exception as e:
            print(f"\n❌ 发生错误: {e}\n")


if __name__ == "__main__":
    main()
