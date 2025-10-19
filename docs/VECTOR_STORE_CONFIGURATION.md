# 向量数据库配置指南

本项目支持多种向量数据库，可以通过配置文件轻松切换。

## 支持的向量数据库

### 1. FAISS (默认推荐)
- **faiss_ip**: FAISS 内积索引（最优性能）
- **faiss_l2**: FAISS L2距离索引
- **faiss_hnsw**: FAISS HNSW索引（适合大规模数据）

### 2. ChromaDB
- **chromadb**: 基于ChromaDB的向量存储，支持持久化

### 3. Memory
- **memory**: 内存向量存储（仅用于测试，不持久化）

## 配置方法

### 在 `core/config.py` 中配置

找到以下配置项：

```python
# 向量存储配置
# 可选值: "auto", "chromadb", "faiss_ip", "faiss_l2", "faiss_hnsw", "memory"
vector_store_type: str = "auto"  # 向量存储类型
chromadb_collection_name: str = "rag_documents"  # ChromaDB集合名称
```

### 配置选项说明

#### 1. 使用自动选择（推荐）
```python
vector_store_type: str = "auto"
```
系统会按照以下优先级自动选择可用的向量数据库：
1. faiss_ip (FAISS内积索引)
2. chromadb (ChromaDB)
3. faiss_l2 (FAISS L2索引)
4. faiss_hnsw (FAISS HNSW索引)
5. memory (内存存储)

#### 2. 指定使用 ChromaDB
```python
vector_store_type: str = "chromadb"
chromadb_collection_name: str = "my_documents"  # 自定义集合名称
```

#### 3. 指定使用 FAISS
```python
vector_store_type: str = "faiss_ip"  # 或 "faiss_l2", "faiss_hnsw"
```

#### 4. 使用内存存储（测试用）
```python
vector_store_type: str = "memory"
```

## 安装依赖

### 安装 FAISS
```bash
# CPU版本
pip install faiss-cpu

# GPU版本（如果有CUDA）
pip install faiss-gpu
```

### 安装 ChromaDB
```bash
pip install chromadb
```

### 安装所有依赖
```bash
pip install -r requirements.txt
```

## 数据存储位置

向量数据库文件将存储在：

```python
vector_db_path: str = "data/vector_store"  # 可在config.py中修改
```

- **FAISS**: 存储为 `faiss_index` 文件
- **ChromaDB**: 存储在指定目录下的 SQLite 数据库

## 切换向量数据库注意事项

### 1. 不同数据库之间不兼容
切换向量数据库类型时，需要重新上传和处理文档。

### 2. 数据备份
在切换前建议备份 `data/` 目录：
```bash
# Windows PowerShell
Copy-Item -Recurse data data_backup
```

### 3. 清空旧数据
如果需要全新开始：
```bash
# Windows PowerShell
Remove-Item -Recurse -Force data/vector_store
Remove-Item -Force data/document_metadata.json
```

### 4. ChromaDB 特定配置
ChromaDB 使用集合（Collection）来组织数据：
- 默认集合名: `rag_documents`
- 可在 `config.py` 中通过 `chromadb_collection_name` 修改
- 一个应用可以使用多个集合

## 性能对比

| 数据库 | 速度 | 内存占用 | 持久化 | 适用场景 |
|--------|------|----------|--------|----------|
| faiss_ip | ⭐⭐⭐⭐⭐ | 中 | ✅ | 生产环境（推荐） |
| faiss_l2 | ⭐⭐⭐⭐⭐ | 中 | ✅ | 生产环境 |
| chromadb | ⭐⭐⭐⭐ | 中 | ✅ | 生产环境，需要高级查询 |
| faiss_hnsw | ⭐⭐⭐⭐ | 高 | ✅ | 大规模数据 |
| memory | ⭐⭐⭐⭐⭐ | 高 | ❌ | 测试开发 |

## 使用示例

### 示例 1: 使用 ChromaDB

**修改 `core/config.py`:**
```python
vector_store_type: str = "chromadb"
chromadb_collection_name: str = "my_rag_docs"
vector_db_path: str = "data/chroma_store"  # ChromaDB存储路径
```

**启动应用:**
```bash
python launcher.py
```

**查看日志:**
```
✅ ChromaDB 可用
OK vector_stores.chromadb_vector_store 加载成功
SUCCESS: RAG服务初始化完成，使用: ChromaDB
📂 从 data/chroma_store 加载ChromaDB向量存储...
```

### 示例 2: 使用 FAISS 内积索引

**修改 `core/config.py`:**
```python
vector_store_type: str = "faiss_ip"
vector_db_path: str = "data/faiss_store"
```

**启动应用:**
```bash
python launcher.py
```

### 示例 3: 自动选择

**修改 `core/config.py`:**
```python
vector_store_type: str = "auto"  # 系统自动选择最优方案
```

## 故障排除

### ChromaDB 无法导入
```bash
pip install chromadb
```

### FAISS 无法导入
```bash
# CPU版本
pip install faiss-cpu

# 或 GPU版本
pip install faiss-gpu
```

### 向量存储加载失败
1. 检查 `data/vector_store` 目录是否存在
2. 检查文件权限
3. 删除旧数据重新开始

### ChromaDB 版本兼容性问题
确保使用兼容版本：
```bash
pip install "chromadb>=0.4.0,<0.5.0"
```

## 高级配置

### 自定义向量存储路径
```python
# 针对不同数据库使用不同路径
if config.vector_store_type == "chromadb":
    config.vector_db_path = "data/chroma_store"
elif config.vector_store_type.startswith("faiss"):
    config.vector_db_path = "data/faiss_store"
```

### 使用环境变量
```bash
# Windows PowerShell
$env:VECTOR_STORE_TYPE="chromadb"
$env:CHROMADB_COLLECTION="prod_docs"
```

然后在 `config.py` 中读取：
```python
import os
vector_store_type: str = os.getenv("VECTOR_STORE_TYPE", "auto")
chromadb_collection_name: str = os.getenv("CHROMADB_COLLECTION", "rag_documents")
```

## 总结

- **开发/测试**: 使用 `"auto"` 或 `"memory"`
- **小规模生产**: 使用 `"faiss_ip"` 或 `"chromadb"`
- **大规模生产**: 使用 `"faiss_hnsw"` 或 `"chromadb"`
- **需要高级查询**: 使用 `"chromadb"`

根据你的具体需求选择合适的向量数据库！
