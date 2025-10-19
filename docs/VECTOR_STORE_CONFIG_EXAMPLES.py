"""
向量数据库配置示例
复制此文件中的配置到 core/config.py 使用
"""

# ============================================================
# 示例 1: 使用 ChromaDB (推荐用于生产环境)
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "chromadb"
    chromadb_collection_name: str = "rag_documents"
    vector_db_path: str = "data/chroma_store"

安装依赖:
    pip install chromadb

特点:
    - 自动持久化
    - 支持高级查询功能
    - 适合生产环境
    - 性能优秀
"""

# ============================================================
# 示例 2: 使用 FAISS 内积索引 (性能最优)
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "faiss_ip"
    vector_db_path: str = "data/faiss_store"

安装依赖:
    pip install faiss-cpu
    # 或 GPU 版本: pip install faiss-gpu

特点:
    - 速度最快
    - 内存占用适中
    - 需要手动保存
    - 适合生产环境
"""

# ============================================================
# 示例 3: 使用 FAISS L2 距离索引
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "faiss_l2"
    vector_db_path: str = "data/faiss_store"

特点:
    - 使用欧氏距离计算相似度
    - 适合某些特定场景
"""

# ============================================================
# 示例 4: 使用 FAISS HNSW 索引 (大规模数据)
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "faiss_hnsw"
    vector_db_path: str = "data/faiss_store"

特点:
    - 适合大规模数据 (百万级以上)
    - 牺牲少量精度换取速度
    - 内存占用较高
"""

# ============================================================
# 示例 5: 使用内存存储 (仅用于测试)
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "memory"

特点:
    - 速度最快
    - 不持久化 (重启丢失)
    - 仅用于开发测试
"""

# ============================================================
# 示例 6: 自动选择 (推荐)
# ============================================================
"""
在 core/config.py 的 Config 类中修改以下配置:

    # 向量存储配置
    vector_store_type: str = "auto"
    vector_db_path: str = "data/vector_store"

特点:
    - 自动选择最优的可用向量存储
    - 优先级: faiss_ip > chromadb > faiss_l2 > faiss_hnsw > memory
    - 适合不确定环境的场景
"""

# ============================================================
# 完整配置示例 (core/config.py)
# ============================================================
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:1.5b"
    ollama_embedding_model: str = "nomic-embed-text"
    
    # FastAPI配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # HTTPS/SSL配置
    enable_https: bool = True
    ssl_cert_path: str = "ssl/server.crt"
    ssl_key_path: str = "ssl/server.key"
    ssl_port: int = 8443
    
    # 聊天配置
    select_history_length: int = 10
    max_history_length: int = 50
    streaming: bool = True
    
    # 数据库配置
    database_url: Optional[str] = None
    vector_db_path: str = "data/vector_store"
    document_metadata_path: str = "data/document_metadata.json"
    upload_path: str = "data/uploads"
    
    # ⭐ 向量存储配置 - 在这里修改 ⭐
    # 可选值: "auto", "chromadb", "faiss_ip", "faiss_l2", "faiss_hnsw", "memory"
    vector_store_type: str = "auto"  # 👈 修改这里选择向量数据库
    chromadb_collection_name: str = "rag_documents"  # ChromaDB集合名称
    
    # 系统提示词
    system_prompt: str = (
        "You are a helpful AI assistant..."
    )
"""

# ============================================================
# 切换向量数据库的步骤
# ============================================================
"""
1. 打开 core/config.py 文件

2. 找到 Config 类中的 vector_store_type 配置项

3. 修改为你想使用的向量数据库类型:
   - "chromadb" - 使用 ChromaDB
   - "faiss_ip" - 使用 FAISS 内积索引
   - "faiss_l2" - 使用 FAISS L2 索引
   - "faiss_hnsw" - 使用 FAISS HNSW 索引
   - "memory" - 使用内存存储
   - "auto" - 自动选择

4. 如果使用 ChromaDB，可以修改集合名称:
   chromadb_collection_name: str = "my_custom_name"

5. 保存文件

6. 重启应用:
   python launcher.py

7. 检查日志确认使用的向量数据库:
   应该看到类似 "SUCCESS: RAG服务初始化完成，使用: ChromaDB" 的日志
"""

# ============================================================
# 常见问题
# ============================================================
"""
Q: 切换向量数据库后，之前的文档还在吗？
A: 不在。不同的向量数据库存储格式不兼容，需要重新上传文档。

Q: 如何备份向量数据库？
A: 备份 data/ 目录即可:
   Copy-Item -Recurse data data_backup

Q: ChromaDB 和 FAISS 哪个更好？
A: 
   - 性能要求高: 选 FAISS (faiss_ip)
   - 需要高级查询: 选 ChromaDB
   - 不确定: 选 "auto"

Q: 如何查看当前使用的向量数据库？
A: 启动应用时查看日志，或运行:
   python tools/test_vector_store_config.py

Q: 安装 ChromaDB 报错？
A: 尝试:
   pip install --upgrade pip
   pip install chromadb

Q: FAISS 无法安装？
A: 尝试:
   pip install faiss-cpu
   # Windows 可能需要安装 Visual C++ 构建工具
"""

if __name__ == "__main__":
    print("=" * 70)
    print("  向量数据库配置示例")
    print("=" * 70)
    print("\n📖 查看此文件的注释，了解如何配置不同的向量数据库\n")
    print("📝 配置文件位置: core/config.py")
    print("🔧 配置项: vector_store_type")
    print("\n可选值:")
    print("  • auto       - 自动选择 (推荐)")
    print("  • chromadb   - ChromaDB 向量存储")
    print("  • faiss_ip   - FAISS 内积索引 (最快)")
    print("  • faiss_l2   - FAISS L2 索引")
    print("  • faiss_hnsw - FAISS HNSW 索引 (大规模)")
    print("  • memory     - 内存存储 (测试用)")
    print("\n📚 详细文档: docs/VECTOR_STORE_CONFIGURATION.md")
    print("🧪 测试配置: python tools/test_vector_store_config.py")
    print("=" * 70)
