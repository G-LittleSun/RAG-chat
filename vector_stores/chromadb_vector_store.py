#!/usr/bin/env python3
"""
ChromaDB向量存储模块 
支持ChromaDB的向量存储实现，提供持久化和相似性搜索功能
"""

import os
import uuid
from typing import List, Tuple, Optional
from langchain.schema import Document


class ChromaDBVectorStore:
    """ChromaDB向量存储实现，支持本地和远程服务器"""
    
    def __init__(self, embeddings, collection_name: str = "default_collection", 
                 store_path: str = "chroma_store",
                 remote_host: str = None,
                 remote_port: int = 8000,
                 use_ssl: bool = False,
                 api_token: str = None):
        """
        初始化 ChromaDB 向量存储
        
        Args:
            embeddings: 嵌入模型
            collection_name: 集合名称
            store_path: 本地存储路径（remote_host 为 None 时使用）
            remote_host: 远程服务器地址（例如: "192.168.1.100" 或 "chromadb.example.com"）
            remote_port: 远程服务器端口，默认 8000
            use_ssl: 是否使用 HTTPS 连接远程服务器
            api_token: API 认证令牌（如果远程服务器需要）
        """
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.store_path = store_path
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.use_ssl = use_ssl
        self.api_token = api_token
        self.store = None    # ChromaDB向量存储实例
        self.collection = None  # ChromaDB集合实例
        self.is_remote = remote_host is not None  # 是否使用远程模式
        
        try:
            import chromadb
            from langchain_community.vectorstores import Chroma
            self.chromadb = chromadb
            self.Chroma = Chroma
            self.available = True
            
            # 显示使用模式
            if self.is_remote:
                protocol = "https" if use_ssl else "http"
                print(f"✅ ChromaDB 可用（远程模式: {protocol}://{remote_host}:{remote_port}）")
            else:
                print(f"✅ ChromaDB 可用（本地模式: {store_path}）")
                
        except ImportError as e:
            print(f"❌ ChromaDB不可用: {e}")
            print("💡 安装提示: pip install chromadb")
            self.available = False
    
    def _get_chroma_client(self):
        """获取 ChromaDB 客户端（本地或远程）"""
        if self.is_remote:
            # 远程客户端
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            return self.chromadb.HttpClient(
                host=self.remote_host,
                port=self.remote_port,
                ssl=self.use_ssl,
                headers=headers if headers else None
            )
        else:
            # 本地客户端
            return self.chromadb.PersistentClient(path=self.store_path)
    
    def create_from_documents(self, documents: List[Document]) -> bool:
        """从文档创建向量存储"""
        if not self.available:
            print("❌ ChromaDB不可用")
            return False
        
        try:
            mode = "远程" if self.is_remote else "本地"
            print(f"🔧 创建ChromaDB向量存储（{mode}模式），处理 {len(documents)} 个文档...")
            
            # 提取文档内容和元数据
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            print(f"📝 提取了 {len(texts)} 个文本块")
            
            if self.is_remote:
                # 远程模式：使用 HttpClient
                print(f"🌐 连接到远程ChromaDB服务器...")
                client = self._get_chroma_client()
                
                self.store = self.Chroma.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas,
                    collection_name=self.collection_name,
                    client=client
                )
            else:
                # 本地模式：使用 persist_directory
                os.makedirs(self.store_path, exist_ok=True)
                
                self.store = self.Chroma.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas,
                    collection_name=self.collection_name,
                    persist_directory=self.store_path
                )
            
            print(f"✅ ChromaDB向量存储创建成功（{mode}模式）")
            return True
            
        except Exception as e:
            print(f"❌ 创建ChromaDB向量存储失败: {e}")
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
            print(f"🔍 在ChromaDB中搜索相似文档，查询: '{query[:50]}...'")
            results = self.store.similarity_search(query, k=k)
            print(f"📄 找到 {len(results)} 个相似文档")
            return results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """相似性搜索并返回分数"""
        if not self.store:
            return []
        
        try:
            print(f"🔍 在ChromaDB中搜索相似文档（带分数），查询: '{query[:50]}...'")
            results = self.store.similarity_search_with_score(query, k=k)
            print(f"📄 找到 {len(results)} 个相似文档（带分数）")
            return results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def similarity_search_with_relevance_scores(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """相似性搜索并返回相关性分数（0-1之间）"""
        if not self.store:
            return []
        
        try:
            print(f"🔍 在ChromaDB中搜索相似文档（相关性分数），查询: '{query[:50]}...'")
            results = self.store.similarity_search_with_relevance_scores(query, k=k)
            print(f"📄 找到 {len(results)} 个相似文档（相关性分数）")
            return results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_info(self) -> dict:
        """获取存储信息"""
        if not self.store:
            return {
                "type": "ChromaDB",
                "collection": self.collection_name,
                "documents": 0,
                "available": self.available,
                "persistent": True,
                "store_path": self.store_path
            }
        
        # 尝试获取文档数量
        doc_count = 0
        try:
            # ChromaDB获取集合信息
            if hasattr(self.store, '_collection') and self.store._collection:
                doc_count = self.store._collection.count()
            elif hasattr(self.store, 'get'):
                # 尝试通过get方法获取所有文档来计算数量
                all_docs = self.store.get()
                if all_docs and 'ids' in all_docs:
                    doc_count = len(all_docs['ids'])
        except Exception as e:
            print(f"⚠️ 获取文档数量失败: {e}")
            
        return {
            "type": "ChromaDB",
            "collection": self.collection_name,
            "documents": doc_count,
            "available": True,
            "persistent": True,
            "store_path": self.store_path
        }
    
    def save(self) -> bool:
        """保存向量存储到磁盘（ChromaDB自动持久化）"""
        if not self.store:
            print("❌ 没有向量存储可保存")
            return False
        
        try:
            print(f"💾 ChromaDB自动持久化到: {self.store_path}")
            # ChromaDB会自动持久化，无需手动保存
            # 但可以调用persist方法确保数据写入磁盘
            if hasattr(self.store, 'persist'):
                self.store.persist()
            elif hasattr(self.store, '_client') and hasattr(self.store._client, 'persist'):
                self.store._client.persist()
            print(f"✅ ChromaDB向量存储保存成功")
            return True
        except Exception as e:
            print(f"❌ 保存ChromaDB失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load(self) -> bool:
        """从磁盘或远程服务器加载向量存储"""
        if not self.available:
            return False
        
        try:
            if self.is_remote:
                # 远程模式
                print(f"🌐 连接到远程ChromaDB服务器 {self.remote_host}:{self.remote_port}...")
                
                client = self._get_chroma_client()
                
                self.store = self.Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    client=client
                )
                
                info = self.get_info()
                print(f"✅ 连接远程ChromaDB成功，包含 {info['documents']} 个文档")
                return True
                
            else:
                # 本地模式
                print(f"📂 从 {self.store_path} 加载ChromaDB向量存储...")
                
                # 检查存储目录是否存在
                if not os.path.exists(self.store_path):
                    print(f"❌ 存储目录不存在: {self.store_path}")
                    return False
                
                # 加载现有的ChromaDB存储
                self.store = self.Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.store_path
                )
                
                # 验证加载是否成功
                info = self.get_info()
                print(f"✅ ChromaDB向量存储加载成功，包含 {info['documents']} 个文档")
                return True
            
        except Exception as e:
            print(f"❌ 加载ChromaDB失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_collection(self) -> bool:
        """删除整个集合"""
        try:
            if self.store and hasattr(self.store, '_client'):
                self.store._client.delete_collection(self.collection_name)
                print(f"✅ 删除集合 '{self.collection_name}' 成功")
                self.store = None
                return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False
    
    def get_collection_info(self) -> dict:
        """获取集合详细信息"""
        if not self.store:
            return {}
        
        try:
            if hasattr(self.store, '_collection'):
                collection = self.store._collection
                return {
                    "name": collection.name,
                    "count": collection.count(),
                    "metadata": getattr(collection, 'metadata', {})
                }
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            
        return {}
    
    def clear(self) -> bool:
        """清空集合中的所有文档"""
        try:
            if self.store and hasattr(self.store, '_collection'):
                # 获取所有文档ID
                all_data = self.store._collection.get()
                if all_data and 'ids' in all_data and all_data['ids']:
                    # 删除所有文档
                    self.store._collection.delete(ids=all_data['ids'])
                    print(f"✅ 清空集合 '{self.collection_name}' 成功")
                    return True
                else:
                    print("ℹ️ 集合已经是空的")
                    return True
        except Exception as e:
            print(f"❌ 清空集合失败: {e}")
            return False


def create_chromadb_store(embeddings, collection_name: str = "default_collection", store_path: str = "chroma_store"):
    """创建ChromaDB向量存储的便捷函数"""
    return ChromaDBVectorStore(embeddings, collection_name, store_path)


# 使用示例
if __name__ == "__main__":
    """
    使用示例：
    
    # 1. 创建embeddings（这里需要你的实际embeddings实现）
    from langchain.embeddings import OpenAIEmbeddings  # 或其他embeddings
    embeddings = OpenAIEmbeddings()
    
    # 2. 创建ChromaDB向量存储
    chroma_store = create_chromadb_store(
        embeddings=embeddings,
        collection_name="my_documents",
        store_path="./my_chroma_db"
    )
    
    # 3. 创建一些测试文档
    from langchain.schema import Document
    documents = [
        Document(page_content="这是第一个文档的内容", metadata={"source": "doc1.txt"}),
        Document(page_content="这是第二个文档的内容", metadata={"source": "doc2.txt"}),
        Document(page_content="这是第三个文档的内容", metadata={"source": "doc3.txt"})
    ]
    
    # 4. 创建向量存储
    if chroma_store.create_from_documents(documents):
        print("向量存储创建成功")
        
        # 5. 保存到磁盘
        chroma_store.save()
        
        # 6. 搜索相似文档
        results = chroma_store.similarity_search("第一个文档", k=2)
        for doc in results:
            print(f"找到文档: {doc.page_content[:50]}...")
        
        # 7. 获取存储信息
        info = chroma_store.get_info()
        print(f"存储信息: {info}")
    """
    print("ChromaDB向量存储实现完成!")
    print("请参考文件末尾的使用示例来使用这个类。")