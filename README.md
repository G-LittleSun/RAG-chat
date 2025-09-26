# 🤖 Ollama RAG Chat - 智能文档问答系统

一个基于FastAPI + Ollama + FAISS的现代化智能对话和文档问答系统，具备HTTPS安全支持和ChatGPT风格界面。

## ✨ 主要特性

### 🎯 核心功能
- **双模式聊天**: 普通AI对话 + 智能文档问答 ⭐
- **文档处理**: 支持PDF、Word(.docx/.doc)、TXT文件上传和解析
- **向量检索**: 基于FAISS-IndexFlatIP的高效语义搜索
- **RAG技术**: 检索增强生成，基于文档内容提供准确答案
- **实时通信**: WebSocket支持的流式对话体验
- **会话管理**: 智能会话历史和上下文管理
- **软删除**: 安全的文档删除和恢复机制

### 🎨 现代界面
- **ChatGPT风格**: 专业的现代化用户界面，完全仿造ChatGPT设计
- **响应式设计**: 完美适配桌面端和移动端
- **双界面支持**: 独立的聊天界面和文档问答界面
- **直观操作**: 拖拽上传、模式切换、实时状态显示
- **统一设计语言**: 所有界面保持一致的视觉风格

### 🔒 安全特性
- **HTTPS支持**: SSL/TLS加密传输保护
- **自动证书**: 自签名证书自动生成和管理
- **安全上传**: 文档上传过程全程加密
- **会话隔离**: 独立的用户会话管理
- **数据保护**: 向量数据库访问控制和临时文件安全处理

### 📚 智能文档功能
- **多格式支持**: PDF, Word(.docx/.doc), 纯文本(.txt)
- **智能分块**: 自动将长文档分割为可处理的片段
- **向量存储**: 使用FAISS进行高效相似性搜索和持久化存储
- **上下文检索**: 基于问题自动检索相关文档片段
- **来源追踪**: 显示回答的参考文档来源

## 📋 系统要求

- Python 3.8+
- Ollama已安装并运行
- DeepSeek-R1:1.5b模型（或其他兼容模型）
- nomic-embed-text嵌入模型

## 🚀 快速开始
### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 确保Ollama运行

```bash
ollama serve
```

### 3. 下载模型

```bash
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text
```

### 4. 启动服务

#### HTTP模式（开发）
```bash
python app.py
```

#### 使用统一启动器（推荐）
```bash
# HTTP模式
python launcher.py

# HTTPS模式
python launcher.py --https

# 仅生成SSL证书
python launcher.py --ssl-only
```

## 🌐 访问方式

### HTTP模式
- **聊天界面**: http://localhost:8000/chat
- **文档问答**: http://localhost:8000/static/rag_chat.html
- **API文档**: http://localhost:8000/docs

### HTTPS模式（推荐）
- **聊天界面**: https://localhost:8443/chat
- **文档问答**: https://localhost:8443/static/rag_chat.html
- **API文档**: https://localhost:8443/docs

### 外部访问
- **HTTP**: http://您的IP:8000/chat
- **HTTPS**: https://您的IP:8443/chat
- 确保防火墙允许相应端口访问

## 📁 项目结构

```
ollama_chatmodel/
├── 📄 app.py                    # FastAPI应用主文件
├── ⚙️  config.py                # 核心配置管理
├── 🚀 launcher.py               # 统一启动器
├── 📋 requirements.txt          # 依赖列表
├── 📖 README.md                 # 项目文档
│
├── 🤖 核心模块/
│   ├── models.py                # AI模型管理（优化版）
│   ├── simple_rag_service.py    # RAG服务（精简版）
│   ├── session_manager.py       # 会话管理
│   ├── ssl_manager.py           # SSL证书管理
│   ├── faiss_integration.py     # FAISS向量集成
│   ├── memory_vector_store.py   # 内存向量存储
│   ├── faiss_vector_store.py    # FAISS向量存储
│   └── vector_config.py         # 向量配置
│
├── 🌐 static/                   # 前端界面
│   ├── chat.html               # 聊天界面
│   └── rag_chat.html           # 文档问答界面
│
├── 🔧 tools/                   # 工具脚本
│   ├── check_https.py          # HTTPS检查
│   ├── diagnostic.py           # 系统诊断
│   └── test_rag.py             # RAG测试
│
├── 📚 docs/                    # 文档资料
├── 🔐 ssl/                     # SSL证书
├── 💾 vector_store/            # 向量数据库存储
└── 📦 __pycache__/             # Python缓存
```

## 🎯 使用指南

### 📝 普通聊天模式
1. 访问聊天界面
2. 直接输入问题开始对话
3. 享受流式AI回复体验

### 📚 文档问答模式
1. 访问文档问答界面
2. 上传PDF/Word/TXT文档
3. 切换到"文档问答"模式
4. 基于文档内容进行智能问答

### 🔒 HTTPS安全访问
1. 首次访问会显示安全警告(自签名证书)
2. 点击"高级" → "继续前往localhost"
3. 数据传输受到SSL加密保护

## ️ API接口

### REST API

#### 发送消息
```http
POST /api/chat
Content-Type: application/json

{
    "message": "你好",
    "session_id": "session_123"
}
```

#### 获取会话列表
```http
GET /api/sessions
```

#### 获取会话历史
```http
GET /api/sessions/{session_id}/history
```

#### 删除会话
```http
DELETE /api/sessions/{session_id}
```

### WebSocket接口

#### HTTP模式
连接地址：`ws://localhost:8000/ws/{session_id}`

#### HTTPS模式
连接地址：`wss://localhost:8443/ws/{session_id}`

发送消息格式：
```json
{
    "message": "用户输入的消息"
}
```

接收消息类型：
- `user_message`: 用户消息确认
- `assistant_start`: AI开始响应
- `assistant_chunk`: AI响应片段（流式）
- `assistant_end`: AI响应结束
- `error`: 错误信息

## ⚙️ 配置说明

编辑 `config.py` 文件进行个性化配置：

```python
@dataclass
class Config:
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:1.5b"
    embed_model: str = "nomic-embed-text"
    
    # 服务器配置
    host: str = "0.0.0.0"  # 允许外部访问
    port: int = 8000       # HTTP端口
    ssl_port: int = 8443   # HTTPS端口
    
    # SSL配置
    use_ssl: bool = False
    ssl_cert_path: str = "ssl/server.crt"
    ssl_key_path: str = "ssl/server.key"
    
    # 聊天配置
    max_history_length: int = 50
    streaming: bool = True
    
    # 向量存储配置
    vector_store_type: str = "faiss"  # "memory" or "faiss"
    faiss_index_type: str = "IndexFlatIP"
```

## 📖 API文档

访问 `http://localhost:8000/docs` 或 `https://localhost:8443/docs` 查看完整的API文档。

### 主要端点
- `GET /` - 系统状态
- `GET /chat` - 聊天界面
- `WebSocket /ws/{session_id}` - 实时聊天
- `POST /api/documents/upload` - 文档上传
- `GET /api/rag/status` - RAG状态检查

## 🔧 开发工具

### 环境检查
```bash
# 检查系统环境
python tools/check_setup.py

# 验证安装
python tools/verify_setup.py

# 系统诊断
python tools/diagnostic.py
```

### 功能测试
```bash
# 测试RAG功能
python tools/test_rag.py

# 检查HTTPS状态
python tools/check_https.py
```

## 🚨 故障排除

### 常见问题
1. **Ollama连接失败**: 确保Ollama服务运行在11434端口
2. **FAISS导入错误**: 运行 `pip install faiss-cpu`
3. **SSL证书问题**: 删除ssl/目录重新生成证书
4. **端口占用**: 检查8000/8443端口是否被占用
5. **模型下载**: 确保已下载 deepseek-r1:1.5b 和 nomic-embed-text

### 支持
- 查看 `docs/` 目录下的详细文档
- 运行诊断工具: `python tools/diagnostic.py`
- 检查日志输出排查问题

## 🔐 SSL证书管理

项目包含智能SSL证书管理系统：

- **自动生成**: 首次启动HTTPS时自动创建证书
- **智能检测**: 自动检查证书有效期
- **多种方法**: 支持OpenSSL和Python cryptography
- **过期提醒**: 证书即将过期时自动更新

### 手动管理证书

```bash
# 生成新证书
python ssl_manager.py

# 强制重新生成
python ssl_manager.py --force

# 或使用启动器
python launcher.py --ssl-only
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License

---

**🌟 享受智能对话和文档问答的全新体验！**

## 📱 移动端使用

1. 确保手机和电脑在同一WiFi网络
2. 在手机浏览器中访问：`https://您的IP:8443/chat`
3. 首次访问HTTPS时接受证书警告
4. 享受移动端优化的聊天体验

## 🔧 扩展开发

项目采用模块化设计，易于扩展：

### 添加新的AI模型

1. 在 `models.py` 中添加新的模型类
2. 更新 `config.py` 中的模型配置
3. 在 `app.py` 中注册新的API端点

### 集成向量数据库

```python
# 在 extensions.py 中添加
from langchain.vectorstores import FAISS

class RAGChatModel(ChatModel):
    def __init__(self, vectorstore_path: str):
        super().__init__()
        self.vectorstore = FAISS.load_local(vectorstore_path)
```

## 🚨 故障排除

### SSL证书问题
- 浏览器显示"不安全"是正常现象（自签名证书）
- 点击"高级"→"继续访问"即可
- 生产环境建议使用CA签名证书

### 连接问题
- 检查Ollama服务是否运行：`ollama serve`
- 验证模型已下载：`ollama list`
- 确认防火墙设置允许相应端口

### 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查Python版本
python --version
```

## 🔄 更新日志

### v3.0.0（当前）
- ✅ **项目清理**: 移除所有测试和调试文件，结构更清晰
- ✅ **软删除功能**: 安全的文档删除和恢复机制
- ✅ **前端优化**: 修复文档删除ID同步问题
- ✅ **数据持久化**: 完善的向量存储加载和保存机制
- ✅ **错误处理**: 全面的错误处理和用户友好提示

### v2.1.0
- ✅ 统一项目结构，清理冗余文件
- ✅ 智能SSL证书管理系统
- ✅ 多种启动方式支持
- ✅ 改进的错误处理和用户体验

### v2.0.0
- ✅ 添加HTTPS/SSL安全支持
- ✅ 重新设计ChatGPT风格界面
- ✅ 增强移动端响应式支持
- ✅ 自动SSL证书生成
- ✅ 安全的WebSocket (WSS)连接

### v1.0.0
- ✅ 基础聊天功能
- ✅ WebSocket实时通信
- ✅ 会话管理
- ✅ REST API接口
- ✅ 模块化架构

## 🎯 功能亮点

### 智能文档处理
- **自动分块**: 长文档智能分割为可处理片段
- **语义搜索**: 基于FAISS的高效向量检索
- **上下文感知**: 根据问题检索最相关的文档内容
- **多文档支持**: 同时处理多个文档，提供综合答案

### 现代化界面体验
- **ChatGPT风格**: 完全模仿ChatGPT的界面设计
- **模式无缝切换**: 普通聊天 ⇄ 文档问答一键切换
- **拖拽上传**: 支持文件拖拽和批量上传
- **实时反馈**: 文档处理状态和连接状态实时显示
- **响应式设计**: 完美适配各种屏幕尺寸

### 安全性保障
- **HTTPS加密**: 全程SSL/TLS加密保护
- **会话隔离**: 独立的用户会话管理
- **数据安全**: 文档内容加密传输和安全存储
- **访问控制**: 向量数据库访问权限控制

## 📞 技术支持

如果您在使用过程中遇到问题，请：
1. 查看上述常见问题解决方案
2. 检查Ollama服务状态和模型可用性
3. 验证Python依赖是否正确安装
4. 确认网络连接和防火墙设置

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！项目结构清晰，代码规范，便于二次开发和定制。

---

**🎉 享受您的智能文档问答体验！**