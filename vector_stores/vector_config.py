#!/usr/bin/env python3
"""
向量存储配置模块 - 精简版
"""

# 向量存储配置
VECTOR_STORES = {
    "memory": {
        "name": "内存向量存储",
        "module": "memory_vector_store",
        "class": "MemoryVectorStore",
        "persistent": False
    },
    "faiss_l2": {
        "name": "FAISS L2索引", 
        "module": "faiss_vector_store",
        "class": "FAISSVectorStore",
        "index_type": "IndexFlatL2",
        "persistent": True
    },
    "faiss_ip": {
        "name": "FAISS 内积索引",
        "module": "faiss_vector_store", 
        "class": "FAISSVectorStore",
        "index_type": "IndexFlatIP",
        "persistent": True
    },
    "faiss_hnsw": {
        "name": "FAISS HNSW索引",
        "module": "faiss_vector_store",
        "class": "FAISSVectorStore", 
        "index_type": "IndexHNSWFlat",
        "persistent": True
    },
    "chromadb": {
        "name": "ChromaDB向量存储",
        "module": "chromadb_vector_store",
        "class": "ChromaDBVectorStore",
        "persistent": True,
        "collection_name": "default_collection"
    }
}

# 默认优先级（首选ChromaDB，然后是FAISS内积索引）
DEFAULT_PRIORITY = ["chromadb", "faiss_ip", "faiss_l2", "faiss_hnsw", "memory"]


def get_store_config(store_type: str = "auto") -> dict:
    """获取向量存储配置"""
    if store_type == "auto":
        return {"type": "auto", "priority": DEFAULT_PRIORITY}
    elif store_type in VECTOR_STORES:
        config = VECTOR_STORES[store_type].copy()
        config["type"] = store_type
        return config
    else:
        raise ValueError(f"不支持的向量存储类型: {store_type}")


def list_available_stores() -> list:
    """列出所有可用的向量存储类型"""
    available = []
    
    # 检查内存存储
    try:
        from langchain_community.vectorstores import DocArrayInMemorySearch
        available.append("memory")
    except ImportError:
        pass
    
    # 检查FAISS存储
    try:
        import faiss
        from langchain_community.vectorstores import FAISS
        available.extend(["faiss_l2", "faiss_ip", "faiss_hnsw"])
    except ImportError:
        pass
    
    # 检查ChromaDB存储
    try:
        import chromadb
        from langchain_community.vectorstores import Chroma
        available.append("chromadb")
    except ImportError:
        pass
    
    return available