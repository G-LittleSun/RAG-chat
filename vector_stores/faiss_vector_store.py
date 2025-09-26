#!/usr/bin/env python3
"""
FAISS向量存储模块 - 精简版
支持多种FAISS索引类型的向量存储实现
"""

import os
from typing import List, Tuple
from langchain.schema import Document


class FAISSVectorStore:
    """FAISS向量存储实现"""
    
    def __init__(self, embeddings, index_type: str = "IndexFlatL2", store_path: str = "vector_store"):
        self.embeddings = embeddings
        self.index_type = index_type
        self.store_path = store_path
        self.store = None    # FAISS向量存储实例
        
        try:
            import faiss
            from langchain_community.vectorstores import FAISS
            self.faiss = faiss
            self.FAISS = FAISS
            self.available = True
        except ImportError as e:
            print(f"❌ FAISS不可用: {e}")
            self.available = False
    
    def create_from_documents(self, documents: List[Document]) -> bool:
        """从文档创建向量存储"""
        if not self.available:
            print("❌ FAISS不可用")
            return False
        
        try:
            print(f"🔧 创建FAISS向量存储，处理 {len(documents)} 个文档...")
            '''page_content: 字符串类型，表示文档的主要内容。
            metadata: 字典类型，用于存储文档的元数据，如来源、页码、标题等。'''
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            print(f"📝 提取了 {len(texts)} 个文本块")
            
            # 根据索引类型选择不同的距离度量
            if self.index_type == "IndexFlatIP":
                print("🔧 使用内积相似度创建向量存储...")
                # 用传入的embeddings 模型将所有 texts 转换为向量,并且绑定metadata。
                self.store = self.FAISS.from_texts(
                    texts,
                    self.embeddings,
                    metadatas=metadatas,
                    distance_strategy="INNER_PRODUCT" 
                    # 内积相似度，值越大越相似
                )
            else:
                print("🔧 使用L2距离创建向量存储...")
                # 默认使用L2距离，衡量两点空间中直线距离，值越小越相似
                self.store = self.FAISS.from_texts(
                    texts,
                    self.embeddings, 
                    metadatas=metadatas
                )
            print("✅ FAISS向量存储创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建FAISS向量存储失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到现有存储"""
        if not self.store:
            print("📝 第一次添加文档，创建新的向量存储...")
            return self.create_from_documents(documents)
        
        try:
            print(f"📝 向现有向量存储添加 {len(documents)} 个文档...")
            self.store.add_documents(documents)
            print("✅ 文档添加成功")
            return True
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """相似性搜索"""
        if not self.store:
            return []
        
        try:
            return self.store.similarity_search(query, k=k)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """相似性搜索并返回分数"""
        if not self.store:
            return []
        
        try:
            # similarity_search_with_score faiss的同名函数
            return self.store.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_info(self) -> dict:
        """获取存储信息"""
        if not self.store:
            return {"type": f"FAISS-{self.index_type}", "documents": 0, "available": self.available}
        
        # 尝试获取文档数量
        doc_count = 0
        try:
            if hasattr(self.store, 'index') and hasattr(self.store.index, 'ntotal'):
                doc_count = self.store.index.ntotal
        except:
            pass
            
        return {
            "type": f"FAISS-{self.index_type}",
            "documents": doc_count,
            "available": True,
            "persistent": True
        }
    
    def save(self) -> bool:
        """保存向量存储到磁盘"""
        if not self.store:
            print("❌ 没有向量存储可保存")
            return False
        
        try:
            print(f"💾 保存向量存储到: {self.store_path}")
            os.makedirs(self.store_path, exist_ok=True)
            save_path = os.path.join(self.store_path, "faiss_index")
            self.store.save_local(save_path)
            print(f"✅ 向量存储保存成功: {save_path}")
            return True
        except Exception as e:
            print(f"❌ 保存FAISS索引失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load(self) -> bool:
        """从磁盘加载向量存储"""
        if not self.available:
            return False
        
        try:
            save_path = os.path.join(self.store_path, "faiss_index")
            # 检查实际的文件名（FAISS保存时会使用index作为前缀）
            index_faiss_path = os.path.join(save_path, "index.faiss")
            index_pkl_path = os.path.join(save_path, "index.pkl")
            
            if os.path.exists(index_faiss_path) and os.path.exists(index_pkl_path):
                self.store = self.FAISS.load_local(save_path, self.embeddings, allow_dangerous_deserialization=True)
                return True
        except Exception as e:
            print(f"加载FAISS索引失败: {e}")
        
        return False


def create_faiss_store(embeddings, index_type: str = "IndexFlatL2", store_path: str = "vector_store"):
    """创建FAISS向量存储的便捷函数"""
    return FAISSVectorStore(embeddings, index_type, store_path)