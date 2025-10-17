# AgenticAI Platform

AgenticAI 是一个面向多智能体 AI 应用的示例项目，当前实现了两个核心能力：

- **对话式 OCR 文档识别**：上传文档或图片，结合 LLM 提供上下文感知的回答。
- **设备运维机器人**：输入设备遥测数据，获得结合知识库的故障排查建议。

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
# 使用 Ollama 暴露的 DeepSeek 模型
# export OLLAMA_MODEL="deepseek-r1:70b"
# PaddleOCR 可选参数
# export OCR_LANG="ch"
# export OCR_USE_GPU=true
uvicorn app.main:app --reload
```

默认会监听 `http://localhost:8000`，对外提供 `/api/chat` 接口。后端基于 PaddleOCR 本地识别图片或 PDF 文档，首次启动会自动下载模型到用户缓存目录，确保磁盘空间充足；如需使用 GPU，请预先安装 PaddlePaddle GPU 版本。

#### 数据持久化

- 所有知识库、维修记录与 OCR 结果默认写入 `storage/` 目录，可通过 `AGENTICAI_DATA_DIR` 环境变量修改位置。
- OCR 解析后的文本与原始文件副本会分别保存为 `.txt`、`.json` 与 `.bin` 文件，便于归档与再次调用。
- 设备运维机器人可通过 API 管理知识库条目与维修记录，所有写入会自动同步到上述目录。

常用接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat` | 与任意 Agent 对话 |
| `GET` | `/api/device-ops/knowledge-base` | 获取知识库全文 |
| `POST` | `/api/device-ops/knowledge-base` | 新增或更新知识库条目 |
| `POST` | `/api/device-ops/maintenance-records` | 记录一次维修操作 |
| `GET` | `/api/device-ops/maintenance-records` | 查询维修历史，支持 `device_id`、`limit` 查询参数 |

> **提示**：`paddleocr` 默认会安装 CPU 版 `paddlepaddle`，如需 GPU 加速请根据 [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR) 安装对应的 CUDA 版本，并在环境中设置 `OCR_USE_GPU=true`。

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
# export OLLAMA_MODEL="deepseek-r1:70b"
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
