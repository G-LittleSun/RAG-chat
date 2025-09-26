#!/usr/bin/env python3
"""
RAG集成模块 - 兼容性包装器
提供向后兼容的接口以便访问新的模块化RAG服务
"""

from typing import List, Dict, Any, Optional, Generator

# 从新的模块化结构中导入所有功能
from core.simple_rag_service import (
    SimpleRAGService,
    DEPENDENCIES_AVAILABLE as VECTOR_STORE_AVAILABLE
)

# 为了兼容性，创建一个DocumentRAGService别名
DocumentRAGService = SimpleRAGService

# 配置选项
VECTOR_STORE_CONFIG = {
    "default": "auto",  # 可以改为 "memory", "faiss_flat_ip", "faiss_flat_l2", "faiss_hnsw", "faiss_ivf"
    "faiss_store_path": "vector_store"
}

# RAG服务实例，全局变量，用于存储 RAG 服务的唯一实例，这是单例模式的核心。
_rag_service = None

def get_rag_service(store_type: str = None, **kwargs):
    """获取RAG服务实例"""
    global _rag_service
    
    if _rag_service is None:
        store_type = store_type or VECTOR_STORE_CONFIG["default"]
        store_path = kwargs.get("store_path", VECTOR_STORE_CONFIG["faiss_store_path"])
        
        try:
            _rag_service = SimpleRAGService(vector_store_type=store_type, store_path=store_path)
        except Exception as e:
            print(f"WARNING RAG服务创建失败: {e}")
            return None
    
    return _rag_service

def is_rag_available():
    """检查RAG是否可用"""
    return VECTOR_STORE_AVAILABLE and get_rag_service() is not None

def process_uploaded_file(file_path: str):
    """处理上传的文件"""
    service = get_rag_service()
    if service:
        return service.process_document(file_path)
    return False

def chat_with_documents(message: str):
    """与文档聊天"""
    service = get_rag_service()
    if service:
        return service.rag_chat(message)
    return "RAG服务不可用"

def chat_with_documents_stream(message: str, history=None):
    """流式与文档聊天"""
    service = get_rag_service()
    if service:
        return service.rag_chat_stream(message)
    return iter(["RAG服务不可用"])

def list_documents():
    """列出所有文档"""
    service = get_rag_service()
    if service:
        status = service.get_status()
        return status.get("vector_store", {}).get("documents", [])
    return []

def delete_document(document_id: str):
    """删除文档"""
    service = get_rag_service()
    if service:
        return service.delete_document(document_id)
    return {
        "success": False,
        "message": "删除失败",
        "error": "RAG服务不可用"
    }

def set_vector_store_type(store_type: str, **kwargs):
    """设置向量存储类型"""
    global _rag_service
    
    # 清除现有服务，强制重新创建
    _rag_service = None
    
    # 更新配置
    VECTOR_STORE_CONFIG["default"] = store_type
    if "store_path" in kwargs:
        VECTOR_STORE_CONFIG["faiss_store_path"] = kwargs["store_path"]
    
    print(f"SUCCESS 向量存储类型已设置为: {store_type}")

def get_current_rag_service():
    """获取当前配置的RAG服务"""
    return get_rag_service(
        VECTOR_STORE_CONFIG["default"],
        store_path=VECTOR_STORE_CONFIG["faiss_store_path"]
    )


if __name__ == "__main__":
    # 测试不同的向量存储类型
    print("🧪 测试模块化RAG服务...")
    
    # 测试内存存储
    print("\n📝 测试内存向量存储:")
    set_vector_store_type("memory")
    service = get_current_rag_service()
    if service:
        info = service.get_store_info()
        print(f"✅ 内存存储: {info}")
    else:
        print("❌ 内存存储不可用")
    
    # 测试FAISS存储（如果可用）
    print("\n📝 测试FAISS向量存储:")
    set_vector_store_type("faiss_flat_ip")
    service = get_current_rag_service()
    if service:
        info = service.get_store_info()
        print(f"✅ FAISS存储: {info}")
    else:
        print("❌ FAISS存储不可用")
    
    print("\n🎉 模块化架构测试完成!")