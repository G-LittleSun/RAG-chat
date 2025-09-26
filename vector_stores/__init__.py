"""
向量存储模块包
包含各种向量存储实现
"""

# 导入向量存储类，提供统一的存储接口
try:
    from .memory_vector_store import MemoryVectorStore
    __all__ = ['MemoryVectorStore']
    print("OK vector_stores.memory_vector_store 加载成功")
except ImportError as e:
    print(f"WARNING memory_vector_store 导入失败: {e}")
    __all__ = []

try:
    from .faiss_vector_store import FAISSVectorStore
    __all__.append('FAISSVectorStore')
    print("OK vector_stores.faiss_vector_store 加载成功")
except ImportError as e:
    print(f"WARNING faiss_vector_store 导入失败: {e}")

# 注意：vector_config 不是类，而是配置模块，不导入到包级别

# 向量存储工厂函数
def create_vector_store(store_type="faiss", embeddings=None, **kwargs):
    """
    创建向量存储实例的工厂函数
    
    Args:
        store_type: 存储类型 ("memory" 或 "faiss")
        embeddings: 嵌入模型实例（必需）
        **kwargs: 传递给存储类的参数
    
    Returns:
        向量存储实例
    """
    if not embeddings:
        raise ValueError("embeddings 参数是必需的")
        
    if store_type.lower() == "memory":
        return MemoryVectorStore(embeddings=embeddings, **kwargs)
    elif store_type.lower() == "faiss":
        if 'FAISSVectorStore' in globals():
            return FAISSVectorStore(embeddings=embeddings, **kwargs)
        else:
            raise ImportError("FAISSVectorStore 未能成功导入")
    else:
        raise ValueError(f"不支持的向量存储类型: {store_type}")

__all__.append('create_vector_store')

# 包信息
__version__ = "1.0.0"
__author__ = "RAG System"