# 🤖 Ollama RAG Chat - 智能文档问答系统

> 基于 FastAPI + Ollama + ChromaDB/FAISS 的现代化 RAG 系统，支持本地部署和远程向量数据库

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 核心特性

- 🤖 **双模式对话**: 普通聊天 + 基于文档的 RAG 问答
- 📚 **多格式支持**: PDF、Word、TXT 文档智能解析
- 🗄️ **灵活向量存储**: 支持 ChromaDB（本地/远程）、FAISS、内存存储
- 🌐 **远程部署**: 支持连接到远程 ChromaDB 服务器，多设备共享数据
- 🔒 **安全通信**: HTTPS/WSS 加密，自动证书管理
- 🎨 **现代界面**: ChatGPT 风格 UI，响应式设计
- ⚡ **流式响应**: WebSocket 实时通信，打字机效果

## � 快速开始

### 系统要求
- Python 3.8+
- Ollama 服务
- 模型：`deepseek-r1:1.5b` + `nomic-embed-text`

### 一键启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Ollama 并下载模型
ollama serve
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text

# 3. 启动应用（HTTPS 模式）
python launcher.py --https
```

### 访问地址

| 服务 | HTTP | HTTPS |
|------|------|-------|
| 聊天界面 | http://localhost:8000/chat | https://localhost:8443/chat |
| 文档问答 | http://localhost:8000/static/rag_chat.html | https://localhost:8443/static/rag_chat.html |
| API 文档 | http://localhost:8000/docs | https://localhost:8443/docs |

## ⚙️ 向量数据库配置

支持多种向量数据库，通过 `core/config.py` 配置：

### 支持的数据库

| 类型 | 性能 | 持久化 | 远程支持 | 适用场景 |
|------|------|--------|----------|----------|
| `chromadb` | ⭐⭐⭐⭐ | ✅ | ✅ | 生产环境（推荐） |
| `faiss_ip` | ⭐⭐⭐⭐⭐ | ✅ | ❌ | 单机高性能 |
| `faiss_l2` | ⭐⭐⭐⭐⭐ | ✅ | ❌ | 单机高性能 |
| `faiss_hnsw` | ⭐⭐⭐⭐ | ✅ | ❌ | 大规模数据 |
| `memory` | ⭐⭐⭐⭐⭐ | ❌ | ❌ | 测试开发 |
| `auto` | - | - | - | 自动选择 |

### 配置示例

#### 本地 ChromaDB（默认）
```python
# core/config.py
vector_store_type: str = "chromadb"
chromadb_remote_host: str = None  # 本地模式
```

#### 远程 ChromaDB（多设备共享）⭐ NEW
```python
# core/config.py
vector_store_type: str = "chromadb"
chromadb_remote_host: str = "192.168.x.xxx"  # 服务器 IP
chromadb_remote_port: int = 8000
chromadb_use_ssl: bool = False
```

#### 远程服务器部署（一行命令）
```bash
# 在数据服务器上运行
docker run -d --name chromadb -p 8000:8000 \
  -v /data/chromadb:/chroma/chroma chromadb/chroma
```

### 详细文档
- 📖 [向量数据库配置指南](docs/VECTOR_STORE_CONFIGURATION.md)
- 🚀 [快速开始](docs/QUICK_START_VECTOR_DB.md)
- 🌐 [远程部署指南](docs/CHROMADB_REMOTE_DEPLOYMENT.md)
- 🧪 测试工具: `python tools/test_vector_store_config.py`

## 📁 项目结构

```
ollama_chatmodel/
├── app.py                      # FastAPI 主应用
├── launcher.py                 # 启动器
├── core/                       # 核心模块
│   ├── config.py              # 配置管理
│   ├── models.py              # AI 模型
│   ├── simple_rag_service.py  # RAG 服务
│   └── session_manager.py     # 会话管理
├── vector_stores/              # 向量存储
│   ├── chromadb_vector_store.py
│   ├── faiss_vector_store.py
│   └── memory_vector_store.py
├── static/                     # 前端界面
├── docs/                       # 项目文档
├── tools/                      # 工具脚本
└── data/                       # 数据存储
```

## 🔧 开发工具

```bash
# 系统诊断
python tools/diagnostic.py

# RAG 测试
python tools/test_rag.py

# 向量存储测试
python tools/test_vector_store_config.py

# 查看 ChromaDB 数据
python tools/view_chromadb.py
```

## 🚨 常见问题

| 问题 | 解决方案 |
|------|---------|
| Ollama 连接失败 | 确保 `ollama serve` 运行在 11434 端口 |
| 向量数据库错误 | `pip install faiss-cpu chromadb` |
| SSL 证书警告 | 点击"高级"→"继续访问"（自签名证书） |
| 端口占用 | 检查 8000/8443 端口，或修改 `core/config.py` |
| 远程连接失败 | 检查防火墙、服务器 IP 和端口配置 |

```bash
# 系统诊断（推荐）
python tools/diagnostic.py
```

## � 更新日志

### v3.1.0 (2025-10-19) ⭐ 最新

**ChromaDB 完整集成**
- ✅ 支持 ChromaDB 本地持久化存储
- ✅ 支持远程 ChromaDB 服务器（局域网/公网）
- ✅ 支持 HTTP/HTTPS 连接和 API 认证
- ✅ 灵活的向量数据库切换（配置文件）
- ✅ 新增 7 个详细文档和 2 个测试工具
- ✅ 支持多设备数据共享

**文档列表**
- [完整配置指南](docs/VECTOR_STORE_CONFIGURATION.md)
- [快速开始](docs/QUICK_START_VECTOR_DB.md)
- [远程部署指南](docs/CHROMADB_REMOTE_DEPLOYMENT.md)
- [配置参考](docs/CHROMADB_CONFIG_REFERENCE.md)
- [更新日志](CHANGELOG.md)

### v3.0.0 (2025-09)
- ✅ 项目清理与优化
- ✅ 软删除功能
- ✅ 前端优化
- ✅ 数据持久化完善

### v2.0.0
- ✅ HTTPS/SSL 支持
- ✅ ChatGPT 风格界面
- ✅ 移动端响应式设计

### v1.0.0
- ✅ 基础功能实现

详见 [CHANGELOG.md](CHANGELOG.md)

## 📚 文档导航

- 📖 [完整文档目录](docs/)
- 🚀 [快速开始指南](docs/QUICK_START_VECTOR_DB.md)
- 🌐 [远程部署教程](docs/CHROMADB_REMOTE_DEPLOYMENT.md)
- ⚙️ [配置参考](docs/CHROMADB_CONFIG_REFERENCE.md)
- 📝 [更新日志](CHANGELOG.md)
- � [提交指南](GIT_COMMIT_GUIDE.md)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**🎉 享受智能文档问答体验！** | [GitHub](https://github.com/G-LittleSun/RAG-chat)