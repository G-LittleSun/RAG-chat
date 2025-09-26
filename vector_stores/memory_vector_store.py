#!/usr/bin/env python3
"""
内存向量存储模块 - 精简版
基于DocArrayInMemorySearch的向量存储实现
"""

from typing import List, Tuple
from langchain.schema import Document


class MemoryVectorStore:
    """内存向量存储实现"""
    
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.store = None
        
        try:
            from langchain_community.vectorstores import DocArrayInMemorySearch
            self.DocArrayInMemorySearch = DocArrayInMemorySearch
            self.available = True
        except ImportError as e:
            print(f"❌ DocArrayInMemorySearch不可用: {e}")
            self.available = False
    
    def create_from_documents(self, documents: List[Document]) -> bool:
        """从文档创建向量存储"""
        if not self.available:
            return False
        
        try:
            self.store = self.DocArrayInMemorySearch.from_documents(documents, self.embeddings)
            return True
        except Exception as e:
            print(f"创建内存向量存储失败: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到现有存储"""
        if not self.store:
            return self.create_from_documents(documents)
        
        try:
            self.store.add_documents(documents)
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """相似性搜索并返回分数"""
        if not self.store:
            return []
        
        try:
            return self.store.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_info(self) -> dict:
        """获取存储信息"""
        if not self.store:
            return {"type": "内存向量存储", "documents": 0, "available": self.available}
        
        # 尝试获取文档数量
        doc_count = 0
        try:
            if hasattr(self.store, 'docstore') and hasattr(self.store.docstore, '_dict'):
                doc_count = len(self.store.docstore._dict)
        except:
            pass
            
        return {
            "type": "内存向量存储",
            "documents": doc_count,
            "available": True
        }


def create_memory_store(embeddings):
    """创建内存向量存储的便捷函数"""
    return MemoryVectorStore(embeddings)