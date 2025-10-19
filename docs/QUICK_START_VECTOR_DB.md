# 向量数据库切换快速指南

## 🚀 快速开始

### 方法 1: 使用 ChromaDB（推荐）

1. **安装 ChromaDB**
```powershell
pip install chromadb
```

2. **修改配置文件 `core/config.py`**

找到这一行：
```python
vector_store_type: str = "auto"  # 向量存储类型
```

改为：
```python
vector_store_type: str = "chromadb"  # 向量存储类型
```

3. **启动应用**
```powershell
python launcher.py
```

4. **验证配置**
查看启动日志，应该看到：
```
✅ ChromaDB 可用
OK vector_stores.chromadb_vector_store 加载成功
SUCCESS: RAG服务初始化完成，使用: ChromaDB
```

✅ 完成！现在你的应用正在使用 ChromaDB。

---

### 方法 2: 使用 FAISS（默认，性能最优）

1. **安装 FAISS**（如果还没安装）
```powershell
pip install faiss-cpu
```

2. **修改配置文件 `core/config.py`**

```python
vector_store_type: str = "faiss_ip"  # 向量存储类型
```

3. **启动应用**
```powershell
python launcher.py
```

✅ 完成！

---

### 方法 3: 自动选择（最简单）

**不需要修改任何配置！**

默认配置 `vector_store_type: str = "auto"` 会自动选择最优的可用向量数据库。

优先级顺序：
1. FAISS 内积索引 (faiss_ip)
2. ChromaDB (chromadb)
3. FAISS L2 索引 (faiss_l2)
4. FAISS HNSW 索引 (faiss_hnsw)
5. 内存存储 (memory)

---

## 📝 配置位置

打开文件：`core/config.py`

找到这个部分：
```python
@dataclass
class Config:
    # ... 其他配置 ...
    
    # 向量存储配置
    # 可选值: "auto", "chromadb", "faiss_ip", "faiss_l2", "faiss_hnsw", "memory"
    vector_store_type: str = "auto"  # 👈 在这里修改
    chromadb_collection_name: str = "rag_documents"  # ChromaDB集合名称
```

---

## 🔄 切换数据库注意事项

⚠️ **重要提示**：切换向量数据库类型后，需要重新上传所有文档！

### 推荐步骤：

1. **备份现有数据**
```powershell
Copy-Item -Recurse data data_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')
```

2. **修改配置**
编辑 `core/config.py` 中的 `vector_store_type`

3. **清理旧数据（可选）**
```powershell
# 删除向量存储
Remove-Item -Recurse -Force data/vector_store

# 删除文档元数据
Remove-Item -Force data/document_metadata.json
```

4. **重启应用**
```powershell
python launcher.py
```

5. **重新上传文档**
访问文档问答界面，重新上传你的文档

---

## 🎯 选择建议

| 场景 | 推荐配置 | 原因 |
|------|----------|------|
| 🚀 生产环境（性能优先） | `faiss_ip` | 速度最快，内存占用适中 |
| 🔍 生产环境（功能丰富） | `chromadb` | 支持高级查询，自动持久化 |
| 🧪 开发测试 | `auto` | 自动选择，省心省力 |
| 💾 大规模数据（100万+向量） | `faiss_hnsw` | 针对大规模优化 |
| ⚡ 快速测试（不需要保存） | `memory` | 最快，但不持久化 |

---

## ✅ 验证配置

### 方法 1: 查看启动日志

启动应用后，查看控制台输出：
```
✅ ChromaDB 可用
SUCCESS: RAG服务初始化完成，使用: ChromaDB
```

### 方法 2: 运行测试脚本

```powershell
cd d:\LLMStudy\LLM\Langchain\ollama_chatmodel
python tools/test_vector_store_config.py
```

### 方法 3: 检查配置示例

```powershell
python docs/VECTOR_STORE_CONFIG_EXAMPLES.py
```

---

## 🐛 常见问题

### 问题 1: ChromaDB 导入失败
```
❌ ChromaDB不可用: No module named 'chromadb'
```

**解决方法**:
```powershell
pip install chromadb
```

### 问题 2: FAISS 导入失败
```
❌ FAISS不可用: No module named 'faiss'
```

**解决方法**:
```powershell
pip install faiss-cpu
```

### 问题 3: 向量存储加载失败
```
❌ 加载ChromaDB失败: ...
```

**解决方法**:
1. 检查 `data/vector_store` 目录权限
2. 删除旧的向量存储文件重新开始
3. 确认配置文件路径正确

### 问题 4: 切换后文档丢失

这是正常的！不同向量数据库的存储格式不兼容。

**解决方法**:
重新上传文档到新的向量数据库

---

## 📚 更多信息

- **详细配置文档**: [VECTOR_STORE_CONFIGURATION.md](VECTOR_STORE_CONFIGURATION.md)
- **配置示例代码**: [VECTOR_STORE_CONFIG_EXAMPLES.py](VECTOR_STORE_CONFIG_EXAMPLES.py)
- **项目主文档**: [../README.md](../README.md)

---

## 💡 示例配置

### 示例 1: 生产环境使用 ChromaDB

```python
# core/config.py
@dataclass
class Config:
    # ... 其他配置 ...
    
    vector_store_type: str = "chromadb"
    chromadb_collection_name: str = "production_docs"
    vector_db_path: str = "data/chroma_production"
```

### 示例 2: 开发环境自动选择

```python
# core/config.py
@dataclass
class Config:
    # ... 其他配置 ...
    
    vector_store_type: str = "auto"  # 自动选择最优方案
    vector_db_path: str = "data/vector_store"
```

### 示例 3: 高性能 FAISS

```python
# core/config.py
@dataclass
class Config:
    # ... 其他配置 ...
    
    vector_store_type: str = "faiss_ip"  # 最快的向量搜索
    vector_db_path: str = "data/faiss_store"
```

---

**🎉 祝你使用愉快！如有问题，请查看详细文档或提交 Issue。**
