# 📚 Ollama RAG Chat - 项目API文档

## 📋 目录
- [项目结构概览](#项目结构概览)
- [Core模块 (核心功能)](#core模块-核心功能)
- [Utils模块 (工具模块)](#utils模块-工具模块)
- [Vector_stores模块 (向量存储)](#vector_stores模块-向量存储)
- [Web API接口](#web-api接口)

---

## 📁 项目结构概览

```
ollama_chatmodel/
├── 🎯 core/                    # 核心业务逻辑
│   ├── config.py              # 全局配置管理
│   ├── models.py              # AI模型封装
│   ├── session_manager.py     # 会话管理
│   └── simple_rag_service.py  # RAG服务核心
├── 🔧 utils/                  # 工具模块
│   ├── faiss_integration.py  # FAISS集成工具
│   └── ssl_manager.py        # SSL证书管理
├── 💾 vector_stores/         # 向量存储模块
│   ├── faiss_vector_store.py # FAISS向量存储实现
│   ├── memory_vector_store.py# 内存向量存储实现
│   └── vector_config.py      # 向量存储配置
├── 🌐 static/                # 前端界面
└── 🔧 tools/                 # 测试工具
```

---

# 🎯 Core模块 (核心功能)

## 📄 config.py - 全局配置管理

### 📋 功能描述

全局配置管理类，采用Pydantic BaseSettings实现配置的验证和管理，支持环境变量自动加载。

### 🔧 主要类和方法

#### `class Config(BaseSettings)`
全局配置类，管理应用的所有配置参数。

**属性列表：**
```python
# Ollama配置
ollama_base_url: str = "http://localhost:11434"
ollama_model: str = "deepseek-r1:1.5b"
embedding_model: str = "nomic-embed-text"

# 服务器配置
host: str = "0.0.0.0"
port: int = 8000
debug: bool = True

# HTTPS/SSL配置
enable_https: bool = True
ssl_cert_path: str = "ssl/server.crt"
ssl_key_path: str = "ssl/server.key"
ssl_port: int = 8443

# 聊天配置
max_history_length: int = 50
streaming: bool = True

# 数据库配置
database_url: Optional[str] = None  # 为后续SQL数据库扩展预留
vector_db_path: str = "data/vector_store"  # FAISS向量数据库路径
document_metadata_path: str = "data/document_metadata.json"  # 文档元数据路径
upload_path: str = "data/uploads"  # 文档上传路径

# 系统提示词
system_prompt: str = "..."
```

**方法：**
- `get_ssl_cert_path() -> str`: 获取SSL证书的绝对路径
- `get_ssl_key_path() -> str`: 获取SSL私钥的绝对路径
- `ssl_files_exist() -> bool`: 检查SSL文件是否存在
- `get_vector_db_path() -> str`: 获取向量数据库的绝对路径
- `get_document_metadata_path() -> str`：获取文档元数据文件的绝对路径
- `get_upload_path(self) -> str`：获取上传目录的绝对路径

---

## 📄 models.py - AI模型封装

### 📋 概述

该模块实现基于Ollama的LLM聊天功能，采用分层架构：**ChatModel**(模型调用) → **ChatSession**(会话管理) → **OllamaModelManager**(模型管理)。

------

### 🔧 ChatModel类

**职责**: 纯模型调用，无状态，可复用

### 核心方法

| 方法                                                         | 功能               | 参数                                                         | 返回值                                                       |
| ------------------------------------------------------------ | ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [generate_response()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 生成完整响应       | [message: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), [context: str = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| [generate_stream_response()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 流式响应生成       | 同上                                                         | [Generator[str, None, None\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| [generate_with_history()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 基于历史的响应     | [message: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), [history: List[Dict\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| [generate_stream_with_history()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 基于历史的流式响应 | 同上                                                         | [Generator[str, None, None\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |

------

## 💬 ChatSession类

**职责**: 会话状态管理，自动维护历史记录

### 历史管理

| 方法                                                         | 功能           | 参数/返回值                                                  |
| ------------------------------------------------------------ | -------------- | ------------------------------------------------------------ |
| [add_message()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 添加消息到历史 | [role: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), [content: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |
| [get_history()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取历史副本   | → [List[Dict[str, str]]]                                     |
| [clear_history()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 清空历史       | `void`                                                       |
| [get_history_summary()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 历史统计       | → [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |

### 对话方法

| 方法                                                         | 功能     | 参数                                                         | 返回值                                                       | 特性         |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ |
| [chat()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 完整对话 | [message: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 自动历史管理 |
| [chat_stream()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 流式对话 | [message: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [Generator[str, None, None\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 实时输出     |
| [chat_with_context()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | RAG问答  | [message: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html), [context: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档问答     |
| [chat_stream_with_context()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 流式RAG  | 同上                                                         | [Generator[str, None, None\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 流式文档问答 |

------

## 🎛️ OllamaModelManager类

**职责**: 多模型实例管理，支持动态切换

### 核心方法

| 方法                                                         | 功能         | 参数                                                         | 返回值                                                       | 特性        |
| ------------------------------------------------------------ | ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------- |
| [get_model()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取模型实例 | [model_name: str = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [ChatModel](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 懒加载+缓存 |
| [switch_model()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 切换当前模型 | [model_name: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | `void`                                                       | 运行时切换  |
| [list_available_models()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 列出可用模型 | `void`                                                       | [List[str\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 模型清单    |
| [get_model_info()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取模型信息 | [model_name: str = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [Dict[str, str\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 状态查询    |
| [clear_model_cache()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 清理模型缓存 | [model_name: str = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | `void`                                                       | 内存管理    |



#### -> `Generator[str, None, None]`

**生成流式响应 `-> Generator[str, None, None]`**.

优点：用户可以立即看到部分响应，类似 ChatGPT 的打字机效果

---

## 📄 session_manager.py - 会话管理

### 📋 概述

多用户会话管理模块，维护用户聊天会话的生命周期，支持会话创建、删除和状态查询。

------

### 🎛️ SessionManager类

**职责**: 管理多个ChatSession实例，提供会话生命周期管理

### 核心方法

| 方法                                                         | 功能           | 参数                                                         | 返回值                                                       | 特性               |
| ------------------------------------------------------------ | -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------ |
| [get_session()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取或创建会话 | [session_id: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [ChatSession](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 懒创建，自动实例化 |
| [delete_session()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 删除指定会话   | [session_id: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [bool](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 成功返回True       |
| [list_sessions()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 列出所有会话ID | `void`                                                       | `List[str]`                                                  | 活跃会话清单       |
| [get_session_count()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取会话数量   | `void`                                                       | [int](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 统计信息           |

### 内部状态

- [self.sessions: Dict[str, ChatSession\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) - 会话实例缓存字典



---

## 📄 simple_rag_service.py - RAG服务核心

### 📋 概述

基于向量检索的文档问答服务，集成FAISS/内存向量存储、Ollama嵌入模型和聊天模型，支持文档上传、智能问答和软删除管理。

------

### 🔧 SimpleRAGService类

### 构造函数

| 方法                                                         | 参数                                                         | 功能             | 备注                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------- | --------------------------- |
| [__init__()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [vector_store_type: str = "auto"](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 向量存储类型选择 | "auto", "memory", "faiss_*" |
|                                                              | [store_path: str = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 存储路径         | 默认使用配置文件路径        |

### 文档处理方法

| 方法                                                         | 参数                                                         | 返回值                                                       | 功能                     | 特性                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------ | ------------------------- |
| [process_document()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [file_path: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [tuple[bool, str\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 处理文档并添加到向量存储 | 支持PDF/TXT，多编码自适应 |
|                                                              | [file_content: bytes = None](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |                                                              |                          | 当前未使用此参数          |
| [delete_document()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [document_id: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [dict](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 软删除文档               | 标记删除，保持向量完整性  |
| [list_documents()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [include_deleted: bool = False](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [list](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 列出文档清单             | 默认过滤已删除文档        |
| [clear_store()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 无                                                           | [dict](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 清空向量存储             | 危险操作，重新创建空存储  |

### RAG问答方法

| 方法                                                         | 参数                                                         | 返回值                                                       | 功能               | 特性                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------ | ------------------------- |
| [rag_chat()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [query: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 基于文档检索的问答 | 智能降级，最多3个文档片段 |
|                                                              | [use_context: bool = True](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |                                                              |                    | 可禁用上下文              |
| [rag_chat_stream()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [query: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [Generator[str, None, None\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 流式RAG问答        | 实时打字机效果            |
|                                                              | [use_context: bool = True](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |                                                              |                    |                           |
| [search_documents()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [query: str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [list](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 搜索相关文档片段   | 自动过滤已删除文档        |
|                                                              | [k: int = 3](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) |                                                              |                    | 搜索3倍结果后筛选         |

### 状态管理方法

| 方法                                                         | 参数 | 返回值                                                       | 功能                | 内容                             |
| ------------------------------------------------------------ | ---- | ------------------------------------------------------------ | ------------------- | -------------------------------- |
| [get_status()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 无   | [dict](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 获取RAG服务完整状态 | 向量存储状态、文档统计、模型信息 |

------

### 📊 返回值格式

### process_document() 返回值

| 字段  | 类型                                                         | 说明         | 示例                |
| ----- | ------------------------------------------------------------ | ------------ | ------------------- |
| `[0]` | [bool](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 处理是否成功 | `True`              |
| `[1]` | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档ID       | `"0"`, `"1"`, `"2"` |

### delete_document() 返回值

| 字段                                                         | 类型                                                         | 说明             | 示例值                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------- | ---------------------------------------- |
| [success](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [bool](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 删除是否成功     | `true`                                   |
| `message`                                                    | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 操作结果信息     | `"文档 'test.pdf' 已成功删除"`           |
| `detail`                                                     | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 成功时的详细说明 | `"文档已被标记为删除，不会在搜索中出现"` |
| `error`                                                      | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 失败时的错误信息 | `"文档ID 999 不存在"`                    |

### list_documents() 返回值

| 字段                                                         | 类型                                                         | 说明         | 示例值                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ | ----------------------------- |
| `id`                                                         | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档唯一标识 | `"0"`                         |
| [name](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档文件名   | `"document.pdf"`              |
| [chunks](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [int](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档分块数量 | `5`                           |
| `timestamp`                                                  | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 上传时间戳   | `"2024-01-01T12:00:00"`       |
| [file_path](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文件路径     | `"data/uploads/document.pdf"` |
| `deleted`                                                    | [bool](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 是否已删除   | `false`                       |

### search_documents() 返回值

| 字段                                                         | 类型                                                         | 说明         | 示例值                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ | ---------------------------------------------- |
| [content](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档内容片段 | `"这是文档的一部分内容..."`                    |
| [metadata](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [dict](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档元数据   | `{"document_id": "0", "filename": "test.pdf"}` |
| [score](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [float](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 相似度分数   | `0.85`                                         |

### get_status() 返回值

| 字段                                                         | 类型                                                         | 说明         | 示例值                |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------ | --------------------- |
| `available`                                                  | [bool](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 服务是否可用 | `true`                |
| [vector_store.type](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 向量存储类型 | `"FAISS-IndexFlatIP"` |
| [vector_store.documents](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [int](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档总数     | `3`                   |
| [vector_store.document_list](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [List[str\]](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 文档ID列表   | `["0", "1", "2"]`     |
| `embedding_model`                                            | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 嵌入模型名称 | `"nomic-embed-text"`  |
| [chat_model](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | [str](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 聊天模型名称 | `"deepseek-r1:1.5b"`  |

------

### ⚡ 核心特性表

| 特性类别       | 功能           | 实现方式                                                     | 优势                           |
| -------------- | -------------- | ------------------------------------------------------------ | ------------------------------ |
| **智能存储**   | 自适应存储选择 | [vector_store_type="auto"](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | FAISS持久化 > 内存存储         |
| **文档处理**   | 多格式支持     | PDF/TXT加载器                                                | 多编码自适应(UTF-8→GBK→Latin1) |
| **软删除机制** | 逻辑删除       | 元数据`deleted`标记                                          | 保持向量索引完整性             |
| **智能检索**   | 过量搜索+过滤  | 搜索3倍结果后筛选                                            | 应对删除文档的检索质量         |
| **容错处理**   | 降级机制       | 检索失败时常识回答                                           | 保证服务可用性                 |
| **流式输出**   | 实时响应       | Generator生成器                                              | 提升用户体验                   |

------

### 🔧 配置依赖表

| 配置项                                                       | 用途           | 默认值/示例                     | 必需 |
| ------------------------------------------------------------ | -------------- | ------------------------------- | ---- |
| [config.ollama_embedding_model](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 嵌入模型       | `"nomic-embed-text"`            | ✅    |
| [config.ollama_base_url](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | Ollama服务地址 | `"http://localhost:11434"`      | ✅    |
| [config.ollama_model](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 聊天模型       | `"deepseek-r1:1.5b"`            | ✅    |
| [config.get_vector_db_path()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 向量数据库路径 | `"data/vector_store"`           | ✅    |
| [config.get_document_metadata_path()](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 元数据文件路径 | `"data/document_metadata.json"` | ✅    |

------

### 🎨 使用示例表

| 使用场景     | 代码示例                                                     | 说明                 |
| ------------ | ------------------------------------------------------------ | -------------------- |
| **文档上传** | [success, doc_id = rag.process_document("doc.pdf")](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 返回处理结果和文档ID |
| **RAG问答**  | `answer = rag.rag_chat("文档说了什么？")`                    | 基于文档内容回答     |
| **流式问答** | `for chunk in rag.rag_chat_stream("详细解释"): print(chunk, end='')` | 实时打字效果         |
| **文档搜索** | [results = rag.search_documents("技术架构", k=5)](vscode-file://vscode-app/d:/VsCode/Microsoft VS Code/resources/app/out/vs/code/electron-browser/workbench/workbench.html) | 检索相关文档片段     |
| **文档删除** | `result = rag.delete_document("0")`                          | 软删除指定文档       |
| **状态查询** | `status = rag.get_status()`                                  | 获取服务完整状态     |

---

# 🔧 Utils模块 (工具模块)

## 📄 faiss_integration.py - FAISS集成工具

### 📋 功能描述

提供FAISS向量数据库的集成工具和便捷函数。

### 🔧 主要函数

#### `is_rag_available() -> bool`
检查RAG功能是否可用

**返回值：**
- `bool` - True表示所有RAG依赖都已安装

**检查的依赖：**
- faiss-cpu
- python-multipart
- pypdf
- python-docx
- unstructured

#### `check_faiss_installation() -> bool`
检查FAISS是否正确安装

**返回值：**
- `bool` - True表示FAISS可用

#### `create_faiss_index(dimension: int = 384) -> Any`
创建FAISS索引

**参数：**
- `dimension: int` - 向量维度 (默认: 384)

**返回值：**
- `Any` - FAISS索引对象

---

## 📄 ssl_manager.py - SSL证书管理

### 📋 功能描述
SSL证书的自动生成、验证和管理工具。

### 🔧 主要类和方法

#### `class SSLCertificateManager`
SSL证书管理器

**初始化参数：**
- `cert_dir: str` - 证书目录 (默认: "ssl")

**方法：**

##### `certificate_exists() -> bool`
检查证书是否存在

**返回值：**
- `bool` - 证书和私钥都存在返回True

##### `certificate_valid(days_ahead: int = 30) -> bool`
检查证书有效性

**参数：**
- `days_ahead: int` - 提前检查天数 (默认: 30)

**返回值：**
- `bool` - 证书有效且在指定天数内不过期返回True

##### `generate_certificate(force_regenerate: bool = False) -> bool`
生成SSL证书

**参数：**
- `force_regenerate: bool` - 强制重新生成 (默认: False)

**返回值：**
- `bool` - 生成成功返回True

**生成的文件：**
- `ssl/server.crt` - SSL证书
- `ssl/server.key` - SSL私钥

##### `get_certificate_info() -> Dict[str, Any]`
获取证书信息

**返回值：**
- `Dict[str, Any]` - 证书详细信息

**返回格式：**
```python
{
    "exists": True,
    "valid": True,
    "subject": "CN=localhost",
    "issuer": "CN=localhost", 
    "not_before": "2023-01-01T00:00:00",
    "not_after": "2024-01-01T00:00:00",
    "days_remaining": 365
}
```

#### `create_ssl_context(cert_dir: str = "ssl") -> ssl.SSLContext`
创建SSL上下文

**参数：**
- `cert_dir: str` - 证书目录

**返回值：**
- `ssl.SSLContext` - SSL上下文对象

---

# 💾 Vector_stores模块 (向量存储)

## 📄 vector_config.py - 向量存储配置

### 📋 功能描述
向量存储的配置管理和工厂模式实现。

### 🔧 主要类和方法

#### `class VectorStoreConfig`
向量存储配置类

**属性：**
```python
store_type: str = "faiss"        # 存储类型
dimension: int = 384             # 向量维度
similarity_metric: str = "cosine" # 相似度度量
persist_directory: str = "data/vector_store"  # 持久化目录
```

#### `create_vector_store(config: VectorStoreConfig, embeddings) -> Any`
向量存储工厂函数

**参数：**
- `config: VectorStoreConfig` - 配置对象
- `embeddings` - 嵌入模型实例

**返回值：**
- `Any` - 向量存储实例

---

## 📄 memory_vector_store.py - 内存向量存储

### 📋 功能描述
基于内存的向量存储实现，适用于小规模数据和快速原型开发。

### 🔧 主要类和方法

#### `class MemoryVectorStore`
内存向量存储类

**初始化参数：**
- `embeddings` - 嵌入模型实例

**方法：**

##### `add_documents(documents: List[str], metadatas: List[Dict] = None) -> List[str]`
添加文档到存储

**参数：**
- `documents: List[str]` - 文档文本列表
- `metadatas: List[Dict]` - 元数据列表（可选）

**返回值：**
- `List[str]` - 文档ID列表

##### `similarity_search(query: str, k: int = 5) -> List[Dict]`
相似度搜索

**参数：**
- `query: str` - 查询文本
- `k: int` - 返回数量

**返回值：**
- `List[Dict]` - 搜索结果

##### `delete_documents(document_ids: List[str]) -> None`
删除文档

**参数：**
- `document_ids: List[str]` - 要删除的文档ID列表

##### `get_store_info() -> Dict[str, Any]`
获取存储信息

**返回值：**
- `Dict[str, Any]` - 存储统计信息

---

## 📄 faiss_vector_store.py - FAISS向量存储

### 📋 功能描述
基于FAISS的高性能向量存储实现，支持大规模向量检索和持久化。

### 🔧 主要类和方法

#### `class FAISSVectorStore`
FAISS向量存储类

**初始化参数：**
- `embeddings` - 嵌入模型实例
- `index_path: str` - 索引文件路径（可选）

**方法：**

##### `add_documents(documents: List[str], metadatas: List[Dict] = None) -> List[str]`
添加文档到FAISS索引

**参数：**
- `documents: List[str]` - 文档文本列表
- `metadatas: List[Dict]` - 元数据列表（可选）

**返回值：**
- `List[str]` - 文档ID列表

**示例：**
```python
store = FAISSVectorStore(embeddings)
doc_ids = store.add_documents(
    ["这是第一个文档", "这是第二个文档"],
    [{"source": "doc1.txt"}, {"source": "doc2.txt"}]
)
```

##### `similarity_search(query: str, k: int = 5, filter: Dict = None) -> List[Dict]`
基于FAISS的相似度搜索

**参数：**
- `query: str` - 查询文本
- `k: int` - 返回数量 (默认: 5)
- `filter: Dict` - 过滤条件（可选）

**返回值：**
- `List[Dict]` - 搜索结果

**返回格式：**
```python
[
    {
        "content": "匹配的文档内容",
        "score": 0.95,
        "metadata": {"source": "doc1.txt", "document_id": "123"}
    }
]
```

##### `save(path: str) -> None`
保存FAISS索引到磁盘

**参数：**
- `path: str` - 保存路径

##### `load(path: str) -> bool`
从磁盘加载FAISS索引

**参数：**
- `path: str` - 索引文件路径

**返回值：**
- `bool` - 加载成功返回True

##### `delete_by_metadata(metadata_filter: Dict) -> int`
根据元数据删除文档

**参数：**
- `metadata_filter: Dict` - 元数据过滤条件

**返回值：**
- `int` - 删除的文档数量

**示例：**
```python
# 删除特定文档ID的所有chunk
deleted_count = store.delete_by_metadata({"document_id": "123"})
```

##### `get_store_info() -> Dict[str, Any]`
获取FAISS存储信息

**返回值：**
- `Dict[str, Any]` - 详细的存储统计

**返回格式：**
```python
{
    "type": "FAISS-IndexFlatIP",
    "documents": 150,
    "index_size": 57600,  # 索引中的向量数量
    "dimension": 384,
    "available": True,
    "persistent": True,
    "memory_usage": "2.3MB"
}
```

---

# 🌐 Web API接口

## 📋 RESTful API概览

### 🏠 页面路由
- `GET /` - 首页重定向到聊天界面
- `GET /chat` - 聊天界面页面
- `GET /ws-test` - WebSocket测试页面

### 💬 聊天API
- `POST /api/chat` - 发送聊天消息
- `GET /api/sessions` - 获取所有会话
- `GET /api/sessions/{session_id}/history` - 获取会话历史
- `DELETE /api/sessions/{session_id}` - 删除会话

### 📚 文档问答API
- `GET /api/rag/status` - 获取RAG服务状态
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 列出所有文档
- `DELETE /api/documents/{document_id}` - 删除文档
- `POST /api/documents/chat` - 基于文档对话
- `POST /api/documents/chat/stream` - 基于文档流式对话
- `POST /api/documents/search` - 搜索文档内容

### 🔌 WebSocket
- `WebSocket /ws/{session_id}` - 实时聊天连接

### 🏥 健康检查
- `GET /health` - 服务健康状态

---

## 📝 使用示例

### 基础聊天示例
```python
# 创建会话管理器
session_manager = SessionManager()
session_id = session_manager.create_session()

# 创建模型管理器
model_manager = OllamaModelManager()

# 发送消息并获取回复
user_message = "你好，世界！"
session_manager.add_message(session_id, "user", user_message)

response = model_manager.generate_response(user_message)
session_manager.add_message(session_id, "assistant", response)
```

### RAG文档问答示例
```python
# 创建RAG服务
rag_service = SimpleRAGService(
    model_name="deepseek-r1:1.5b",
    embedding_model="nomic-embed-text",
    vector_store_type="faiss"
)

# 添加文档
doc_id = rag_service.add_document("important_document.pdf")

# 进行问答
answer = rag_service.generate_answer("文档中提到的重点是什么？")
print(answer)
```

### SSL证书管理示例
```python
# 创建SSL管理器
ssl_manager = SSLCertificateManager()

# 检查证书状态
if not ssl_manager.certificate_valid():
    # 生成新证书
    success = ssl_manager.generate_certificate()
    if success:
        print("SSL证书生成成功")
```

---

## ⚡ 性能特性

- **异步处理**: 所有I/O操作采用async/await模式
- **流式响应**: 支持实时流式文本生成
- **向量缓存**: FAISS索引支持持久化缓存
- **会话管理**: 高效的内存会话管理
- **软删除**: 文档删除采用软删除机制，支持恢复

---

## 🔐 安全特性

- **HTTPS支持**: 自动SSL证书生成和管理
- **会话隔离**: 每个用户独立的会话空间
- **输入验证**: Pydantic模型验证所有输入参数
- **错误处理**: 完善的异常处理和用户友好提示

---

**文档版本**: v3.0.0  
**最后更新**: 2025年9月23日