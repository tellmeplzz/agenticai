# AgenticAI Platform

AgenticAI 是一个面向多智能体 AI 应用的示例项目，当前实现了两个核心能力：

- **对话式 OCR 文档识别**：上传文档或图片，结合 LLM 提供上下文感知的回答。
- **设备运维机器人**：输入设备遥测数据，获得结合知识库的故障排查建议。
- **统一会话上下文管理**：后端提供异步 Agent 接口和统一的上下文返回值，前端可直接复用服务端上下文，形成连续对话体验。

项目采用前后端分离的结构，方便后续扩展新的 Agent 功能或替换底层模型。后端基于 FastAPI，前端提供 Streamlit 界面。

## 目录结构

```
backend/
  app/
    agents/           # 各类 Agent 实现
    api/              # FastAPI 路由
    core/             # 配置与常量
    schemas/          # Pydantic 数据模型
    services/         # OCR、设备运维、LLM 等服务封装
  requirements.txt
frontend/
  streamlit_app.py    # 前端应用入口
  requirements.txt
```

## 快速开始

### 1. 后端服务

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认会监听 `http://localhost:8000`，对外提供 `/api/chat` 接口。

> ⚠️ 当前 OCR 与设备运维逻辑包含模拟实现，便于结构演示。将来可以替换为真实 OCR 引擎（如 PaddleOCR、EasyOCR）或接入实际运维系统。

### 2. 前端界面

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

在浏览器打开 `http://localhost:8501`，即可看到统一的 Agent 控制界面。

### 3. 集成 Ollama / 其他 LLM

后端默认调用 `http://localhost:11434/api/generate`。在生产环境可通过环境变量覆盖：

```bash
export OLLAMA_BASE_URL="http://your-ollama-host:11434"
```

也可以在 `LLMService` 中替换为任意兼容接口（如 OpenAI、Azure OpenAI）。

## 扩展新的 Agent

1. 在 `backend/app/agents/` 中创建新的 Agent 类，实现 `BaseAgent`。
2. 如需要外部依赖，在 `services/` 中编写对应服务并注入。
3. 在 `services/agent_registry.py` 的 `build_registry` 中注册新的 agent id。
4. 前端在 `streamlit_app.py` 中增加选择项和特定 UI。

## 测试接口

运行后端后，可使用 curl 测试：

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "device_ops",
    "message": "设备风扇报警，怎么办？",
    "context": {"telemetry": {"temperature": "90C", "uptime": "72h"}}
  }'
```

## 许可证

MIT
