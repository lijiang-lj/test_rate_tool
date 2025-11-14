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

import os
import json
from flask import Flask, request, Response
import requests

app = Flask(__name__)

# ====== 从环境变量读取 Azure 配置 ======
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://xplatform-openai-shared.openai.azure.com/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# 拼出 Azure chat completions 完整 URL
AZURE_CHAT_COMPLETIONS_URL = (
    f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/"
    f"{AZURE_OPENAI_DEPLOYMENT}/chat/completions"
    f"?api-version={AZURE_OPENAI_API_VERSION}"
)

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions_proxy():
    # 1. 拿到 Cline 发来的 JSON
    body = request.get_json(force=True, silent=True) or {}

    # 2. 把 max_tokens 换成 max_completion_tokens（GPT-5 / 新 Azure 模型要求）
    #    参考官方/社区说明，GPT-5 不再支持 max_tokens 
    if "max_tokens" in body:
        body["max_completion_tokens"] = body.pop("max_tokens")

    # 3. 构造发往 Azure 的请求
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY,
    }

    try:
        azure_resp = requests.post(
            AZURE_CHAT_COMPLETIONS_URL,
            headers=headers,
            json=body,
            timeout=60,
        )
    except requests.RequestException as e:
        # 网络或其他异常时，返回 502 给 Cline
        return Response(
            json.dumps({"error": f"Proxy request failed: {str(e)}"}),
            status=502,
            mimetype="application/json",
        )

    # 4. 把 Azure 的响应原样转发回去（状态码 + body）
    return Response(
        response=azure_resp.content,
        status=azure_resp.status_code,
        mimetype=azure_resp.headers.get("Content-Type", "application/json"),
    )

if __name__ == "__main__":
    # 监听本地 8000 端口
    app.run(host="127.0.0.1", port=8000)
#     # 
# pip install flask requests
# python azure_proxy.py
