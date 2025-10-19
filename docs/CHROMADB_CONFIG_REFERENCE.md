# ChromaDB 配置快速参考

## 🎯 三种使用模式

### 模式 1: 本地存储（默认）

**适用场景**: 个人使用，单机开发

**配置 `core/config.py`:**
```python
vector_store_type: str = "chromadb"
chromadb_collection_name: str = "rag_documents"
vector_db_path: str = "data/vector_store"

# 远程配置保持默认
chromadb_remote_host: Optional[str] = None  # 👈 None = 本地模式
```

**特点:**
- ✅ 速度最快
- ✅ 无需网络
- ✅ 数据在本地
- ❌ 仅限单机使用

---

### 模式 2: 远程服务器（局域网）

**适用场景**: 多台电脑共享数据，团队协作

**配置 `core/config.py`:**
```python
vector_store_type: str = "chromadb"
chromadb_collection_name: str = "rag_documents"

# 远程服务器配置
chromadb_remote_host: str = "192.168.x.xxx"  # 👈 局域网服务器 IP
chromadb_remote_port: int = 8000
chromadb_use_ssl: bool = False
chromadb_api_token: Optional[str] = None
```

**服务器端部署:**
```bash
# 一行命令启动
docker run -d --name chromadb -p 8000:8000 -v /data/chromadb:/chroma/chroma chromadb/chroma
```

**特点:**
- ✅ 多设备共享
- ✅ 数据集中管理
- ✅ 局域网速度快
- ❌ 需要服务器

---

### 模式 3: 远程服务器（公网）

**适用场景**: 跨地域访问，云端部署

**配置 `core/config.py`:**
```python
vector_store_type: str = "chromadb"
chromadb_collection_name: str = "rag_documents"

# 公网服务器配置
chromadb_remote_host: str = "chromadb.example.com"  # 👈 域名或公网 IP
chromadb_remote_port: int = 8000
chromadb_use_ssl: bool = True  # 👈 公网建议开启 HTTPS
chromadb_api_token: Optional[str] = "your-api-token"  # 👈 建议添加认证
```

**服务器端配置:**
```bash
# 使用 Docker Compose + Nginx + SSL
# 详见 docs/CHROMADB_REMOTE_DEPLOYMENT.md
```

**特点:**
- ✅ 随时随地访问
- ✅ 高可用性
- ✅ 专业运维
- ❌ 需要公网服务器
- ❌ 延迟可能较高

---

## 📋 配置对照表

| 配置项 | 本地模式 | 局域网远程 | 公网远程 |
|--------|----------|------------|----------|
| `chromadb_remote_host` | `None` | `"192.168.x.xxx"` | `"chromadb.example.com"` |
| `chromadb_remote_port` | - | `8000` | `8000` 或 `443` |
| `chromadb_use_ssl` | - | `False` | `True` |
| `chromadb_api_token` | - | `None` | `"token"` (推荐) |
| `vector_db_path` | `"data/vector_store"` | - | - |

---

## 🔄 快速切换模式

### 从本地切换到远程

**步骤:**
1. 部署远程服务器（见 [CHROMADB_REMOTE_DEPLOYMENT.md](CHROMADB_REMOTE_DEPLOYMENT.md)）
2. 修改 `core/config.py`:
   ```python
   chromadb_remote_host: str = "192.168.x.xxx"  # 改为服务器 IP
   ```
3. 重启应用: `python launcher.py`
4. **重新上传文档**（远程服务器是新的数据库）

### 从远程切换回本地

**步骤:**
1. 修改 `core/config.py`:
   ```python
   chromadb_remote_host: str = None  # 改为 None
   ```
2. 重启应用
3. 如需恢复数据，从备份还原本地 `data/vector_store`

---

## 🧪 测试配置

### 测试 1: 验证本地模式

```powershell
# 启动应用
python launcher.py

# 查看日志
# 应该看到: ✅ ChromaDB 可用（本地模式: data/vector_store）
```

### 测试 2: 验证远程连接

```powershell
# 测试服务器连通性
Invoke-WebRequest -Uri "http://192.168.x.xxx:8000/api/v1/heartbeat"

# 启动应用
python launcher.py

# 查看日志
# 应该看到: ✅ ChromaDB 可用（远程模式: http://192.168.x.xxx:8000）
```

### 测试 3: Python 脚本测试

```python
import chromadb
from core.config import config

if config.chromadb_remote_host:
    # 远程模式
    client = chromadb.HttpClient(
        host=config.chromadb_remote_host,
        port=config.chromadb_remote_port
    )
    print(f"连接到远程: {config.chromadb_remote_host}")
else:
    # 本地模式
    client = chromadb.PersistentClient(path=config.get_vector_db_path())
    print(f"使用本地: {config.get_vector_db_path()}")

# 测试连接
print(f"心跳: {client.heartbeat()}")
print(f"集合数: {len(client.list_collections())}")
```

---

## 💡 使用建议

### 个人开发者
```python
# 推荐：本地模式
chromadb_remote_host: str = None
```

### 小团队（2-5人）
```python
# 推荐：局域网远程
chromadb_remote_host: str = "192.168.x.xxx"
chromadb_use_ssl: bool = False
```

### 大团队/企业
```python
# 推荐：公网远程 + SSL + 认证
chromadb_remote_host: str = "chromadb.company.com"
chromadb_use_ssl: bool = True
chromadb_api_token: str = "secure-token"
```

---

## ⚠️ 注意事项

### 1. 数据不互通
- 本地和远程是**不同的数据库**
- 切换模式后需要**重新上传文档**

### 2. 网络延迟
- 远程模式依赖网络
- 建议局域网使用，公网谨慎

### 3. 数据安全
- 公网部署**必须启用 HTTPS**
- 建议添加 API 认证
- 定期备份数据

### 4. 防火墙配置
- 确保服务器端口 8000 开放
- 云服务器需配置安全组

---

## 🎓 学习资源

- **完整部署指南**: [CHROMADB_REMOTE_DEPLOYMENT.md](CHROMADB_REMOTE_DEPLOYMENT.md)
- **配置说明**: [VECTOR_STORE_CONFIGURATION.md](VECTOR_STORE_CONFIGURATION.md)
- **快速开始**: [QUICK_START_VECTOR_DB.md](QUICK_START_VECTOR_DB.md)
- **ChromaDB 官方文档**: https://docs.trychroma.com/

---

## 📞 故障排除

### 问题 1: 远程连接失败
```
❌ 连接远程ChromaDB失败
```
**解决:**
1. 检查服务器是否运行: `curl http://IP:8000/api/v1/heartbeat`
2. 检查防火墙: `telnet IP 8000`
3. 检查 IP 地址配置是否正确

### 问题 2: 认证失败
```
❌ Authentication failed
```
**解决:**
1. 确认 `chromadb_api_token` 配置正确
2. 检查服务器端认证配置

### 问题 3: 数据丢失
```
✅ 连接远程ChromaDB成功，包含 0 个文档
```
**解决:**
- 这是正常的，远程是新数据库
- 重新上传文档即可

---

**配置完成后，运行 `python launcher.py` 启动应用！** 🚀
