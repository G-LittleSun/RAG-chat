# 📁 项目文件结构总览

## 🎯 整体架构

```
ollama_chatmodel/                    # 项目根目录
├── 🚀 app.py                       # FastAPI主应用 - Web服务入口
├── 🎛️  launcher.py                 # 统一启动器 - 命令行启动工具
├── 📋 requirements.txt              # Python依赖列表
├── 📖 README.md                     # 项目说明文档
├── 📚 API_DOCUMENTATION.md         # 核心模块API文档
└── 🌐 WEB_API_DOCUMENTATION.md     # Web接口API文档
│
├── 🎯 core/                        # 核心业务模块
│   ├── 📄 __init__.py
│   ├── ⚙️  config.py               # 全局配置管理
│   ├── 🤖 models.py                # AI模型封装
│   ├── 💬 session_manager.py       # 会话管理
│   └── 🧠 simple_rag_service.py    # RAG服务核心
│
├── 🔧 utils/                       # 工具模块
│   ├── 📄 __init__.py
│   ├── 🔍 faiss_integration.py     # FAISS集成工具
│   └── 🔐 ssl_manager.py           # SSL证书管理
│
├── 💾 vector_stores/               # 向量存储模块
│   ├── 📄 __init__.py
│   ├── 🗂️  faiss_vector_store.py   # FAISS向量存储实现
│   ├── 💭 memory_vector_store.py   # 内存向量存储实现
│   └── ⚙️  vector_config.py        # 向量存储配置
│
├── 🌐 static/                      # 前端界面文件
│   ├── 💬 chat.html               # 基础聊天界面
│   ├── 📚 rag_chat.html           # 文档问答界面
│   └── 🔌 ws-test.html            # WebSocket测试页面
│
├── 🔧 tools/                       # 开发测试工具
│   ├── 🏥 diagnostic.py           # 系统诊断工具
│   ├── 🔍 check_setup.py          # 环境检查工具
│   ├── 🔒 check_https.py          # HTTPS检查工具
│   └── 🧪 test_*.py               # 各种功能测试脚本
│
├── 💾 data/                        # 数据存储目录
│   ├── 📁 uploads/                # 上传文件存储
│   ├── 🗂️  vector_store/          # 向量数据库文件
│   └── 📊 metadata/               # 文档元数据
│
├── 🔐 ssl/                         # SSL证书目录
│   ├── 📜 server.crt              # SSL证书
│   └── 🔑 server.key              # SSL私钥
│
└── 📚 docs/                        # 文档目录（可选删除）
    └── *.md                       # 各种开发文档
```

---

## 📋 核心文件详解

### 🚀 主应用文件

#### `app.py` - FastAPI主应用
- **作用**: Web服务的主入口，定义所有HTTP API和WebSocket接口
- **核心功能**: 
  - RESTful API路由定义
  - WebSocket实时通信
  - 中间件和错误处理
  - 静态文件服务
- **依赖**: core, utils, vector_stores模块
- **启动**: 可独立启动，但推荐使用launcher.py

#### `launcher.py` - 统一启动器
- **作用**: 提供用户友好的启动方式，支持HTTP/HTTPS模式切换
- **核心功能**:
  - 命令行参数处理
  - SSL证书自动管理
  - 环境检查和错误提示
  - 多种启动模式支持
- **优势**: 比直接运行app.py更稳定和用户友好

---

## 🎯 Core模块详解

### ⚙️ `config.py` - 全局配置
```python
# 主要配置项
class Config:
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:1.5b" 
    embedding_model: str = "nomic-embed-text"
    enable_https: bool = True
    port: int = 8000
    ssl_port: int = 8443
```

### 🤖 `models.py` - AI模型封装
```python
# 核心类
class OllamaModelManager:
    def generate_response(message: str) -> str
    def generate_stream(message: str) -> Iterator[str]
    def is_available() -> bool
```

### 💬 `session_manager.py` - 会话管理
```python
# 核心类
class SessionManager:
    def create_session() -> str
    def add_message(session_id, role, content)
    def get_history(session_id) -> List[Dict]
    def delete_session(session_id) -> bool
```

### 🧠 `simple_rag_service.py` - RAG服务核心
```python
# 核心类
class SimpleRAGService:
    def process_document(file_path: str) -> tuple[bool, str]
    def rag_chat(query: str) -> str
    def search_documents(query: str) -> list
    def delete_document(doc_id: str) -> dict
    def list_documents() -> list
```

---

## 🔧 Utils模块详解

### 🔍 `faiss_integration.py` - FAISS集成
```python
# 主要函数
def is_rag_available() -> bool          # 检查RAG依赖
def check_faiss_installation() -> bool  # 检查FAISS安装
def create_faiss_index(dimension) -> Any # 创建FAISS索引
```

### 🔐 `ssl_manager.py` - SSL证书管理
```python
# 核心类
class SSLCertificateManager:
    def certificate_exists() -> bool
    def certificate_valid(days_ahead=30) -> bool
    def generate_certificate() -> bool
    def get_certificate_info() -> Dict
```

---

## 💾 Vector_stores模块详解

### 🗂️ `faiss_vector_store.py` - FAISS存储
```python
# 核心类
class FAISSVectorStore:
    def add_documents(documents, metadatas) -> List[str]
    def similarity_search(query, k=5) -> List[Dict]
    def save(path: str) -> None
    def load(path: str) -> bool
    def delete_by_metadata(filter) -> int
```

### 💭 `memory_vector_store.py` - 内存存储
```python
# 核心类  
class MemoryVectorStore:
    def add_documents(documents) -> List[str]
    def similarity_search(query, k=5) -> List[Dict]
    def delete_documents(doc_ids) -> None
    def get_store_info() -> Dict
```

### ⚙️ `vector_config.py` - 存储配置
```python
# 配置类
class VectorStoreConfig:
    store_type: str = "faiss"
    dimension: int = 384
    similarity_metric: str = "cosine"
    persist_directory: str = "data/vector_store"
```

---

## 🌐 前端界面文件

### 💬 `chat.html` - 基础聊天界面
- **功能**: 纯AI聊天，不涉及文档问答
- **特点**: ChatGPT风格界面，WebSocket实时通信
- **适用**: 简单AI对话场景

### 📚 `rag_chat.html` - 文档问答界面  
- **功能**: 完整的RAG功能，支持文档上传和问答
- **特点**: 
  - 双模式切换（普通聊天/文档问答）
  - 拖拽文件上传
  - 文档管理（列表、删除）
  - 实时状态指示
- **适用**: 需要基于文档内容问答的场景

### 🔌 `ws-test.html` - WebSocket测试
- **功能**: WebSocket连接测试和调试
- **适用**: 开发调试场景

---

## 🔧 开发工具文件

### 🏥 `diagnostic.py` - 系统诊断
```python
# 主要功能
def check_ollama_connection()     # 检查Ollama连接
def check_model_availability()    # 检查模型可用性  
def check_dependencies()          # 检查Python依赖
def generate_diagnostic_report()  # 生成诊断报告
```

### 🔍 `check_setup.py` - 环境检查
```python
# 检查项目
def check_python_version()        # Python版本检查
def check_ollama_installation()   # Ollama安装检查
def check_required_packages()     # 必需包检查
def verify_configuration()        # 配置验证
```

### 🧪 测试脚本系列
- `test_ollama.py` - Ollama连接测试
- `test_faiss.py` - FAISS功能测试
- `test_rag.py` - RAG端到端测试
- `test_websocket.py` - WebSocket测试
- `test_*.py` - 其他功能模块测试

---

## 💾 数据存储结构

### 📁 `data/` 目录结构
```
data/
├── uploads/                     # 用户上传的原始文件
│   ├── 3a53db2f_111.txt       # 带前缀的原始文件
│   └── 465b135d_222.pdf
├── vector_store/               # 向量数据库存储
│   └── faiss_index/
│       ├── index.faiss         # FAISS索引文件
│       └── index.pkl           # 元数据pickle文件
└── metadata/                   # 文档元数据
    └── documents_metadata.json # 文档信息JSON
```

### 🔐 `ssl/` 证书存储
```
ssl/
├── server.crt                 # SSL证书（自签名）
└── server.key                 # SSL私钥
```

---

## 🔄 数据流程图

### 📚 文档上传流程
```
用户上传文件 → app.py:/api/documents/upload 
            → simple_rag_service.process_document()
            → 文档解析和分块
            → 向量化embedding
            → faiss_vector_store.add_documents()
            → 保存到data/vector_store/
            → 更新metadata
```

### 💬 RAG问答流程  
```
用户问题 → app.py:/api/documents/chat
        → simple_rag_service.rag_chat()
        → 问题向量化
        → faiss_vector_store.similarity_search()
        → 检索相关文档片段
        → 构造prompt
        → models.generate_response()
        → 返回答案
```

### 🔌 WebSocket通信流程
```
前端连接 → app.py:/ws/{session_id}
        → session_manager.create_session()
        → 建立WebSocket连接
        → 接收消息 → 处理 → 流式返回
        → 保存到会话历史
```

---

## ⚡ 性能优化点

### 🚀 核心优化
1. **异步处理**: 所有I/O操作使用async/await
2. **向量缓存**: FAISS索引持久化，避免重复计算
3. **流式响应**: WebSocket和HTTP流式支持
4. **会话复用**: 智能会话管理，减少资源占用

### 💾 存储优化
1. **软删除机制**: 文档删除使用标记而非物理删除
2. **批量处理**: 支持批量文档上传和处理
3. **元数据分离**: 文档内容和元数据分开存储

---

## 🔐 安全考虑

### 🛡️ 安全特性
1. **HTTPS加密**: SSL/TLS全程加密
2. **输入验证**: Pydantic模型验证所有输入
3. **文件类型检查**: 严格的文件格式验证
4. **会话隔离**: 独立的用户会话空间
5. **错误屏蔽**: 不向用户暴露系统内部错误

### 🚨 安全注意事项
- 自签名证书仅适用于开发环境
- 生产环境需要配置防火墙和反向代理
- 敏感文档需要额外的访问控制

---

## 📈 扩展性设计

### 🔧 模块化架构
- **插件化向量存储**: 支持FAISS/Memory多种后端
- **可配置嵌入模型**: 支持不同的embedding模型
- **灵活的文档处理**: 易于添加新的文档格式支持

### 🚀 水平扩展
- **无状态设计**: 服务本身无状态，便于集群部署
- **外部存储**: 向量数据和文件可迁移到外部存储
- **负载均衡**: 支持多实例负载均衡

---

**文档版本**: v3.0.0  
**最后更新**: 2025年9月23日