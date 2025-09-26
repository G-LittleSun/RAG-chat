#!/usr/bin/env python3
"""
简化的RAG服务模块 - 精简版
整合向量存储和文档处理功能
"""

from typing import List, Generator
from pathlib import Path
from datetime import datetime

try:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ RAG服务依赖不可用: {e}")
    DEPENDENCIES_AVAILABLE = False

from .config import config
from .models import ChatModel
from vector_stores.memory_vector_store import MemoryVectorStore
from vector_stores.faiss_vector_store import FAISSVectorStore
from vector_stores.vector_config import get_store_config, list_available_stores


class SimpleRAGService:
    """简化的RAG服务"""
    
    def __init__(self, vector_store_type: str = "auto", store_path: str = None):
        if not DEPENDENCIES_AVAILABLE:    # 依赖包不可用
            raise ImportError("RAG服务依赖不可用")
        
        # 初始化嵌入模型
        self.embeddings = OllamaEmbeddings(
            base_url=config.ollama_base_url,
            model=config.ollama_embedding_model
        )
        
        # 使用配置文件中的路径，如果未指定的话
        self.store_path = store_path or config.get_vector_db_path()
        
        # 初始化向量存储
        self.vector_store = self._create_vector_store(vector_store_type, self.store_path)
        self.vector_store_type = vector_store_type
        
        # 文档跟踪 - 使用配置中的元数据路径
        # 确保data目录存在
        data_dir = Path(config.get_vector_db_path()).parent
        data_dir.mkdir(exist_ok=True)
        
        self.metadata_file_path = Path(config.get_document_metadata_path())
        self.document_metadata = self._load_document_metadata()  # 尝试加载已保存的metadata
        self.next_doc_id = self._get_next_doc_id()  # 基于现有metadata确定下一个ID
        
        # 初始化聊天模型
        self.chat_model = ChatModel()
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        print(f"SUCCESS: RAG服务初始化完成，使用: {self._get_current_store_name()}")
    
    def _load_document_metadata(self):
        """加载文档metadata"""
        try:
            import json
            if Path(self.metadata_file_path).exists():
                with open(self.metadata_file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    print(f"📂 已加载 {len(metadata)} 个文档的metadata")
                    return metadata
        except Exception as e:
            print(f"⚠️  加载metadata时出错: {e}")
        return {}
    
    def _save_document_metadata(self):
        """保存文档metadata"""
        try:
            import json
            with open(self.metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存metadata时出错: {e}")
    
    def _get_next_doc_id(self):
        """基于现有metadata确定下一个文档ID"""
        if not self.document_metadata:
            return 0
        # 找到最大的数字ID并加1
        max_id = -1
        for doc_id in self.document_metadata.keys():
            try:
                num_id = int(doc_id)
                max_id = max(max_id, num_id)
            except ValueError:
                pass  # 忽略非数字ID
        return max_id + 1
    
    def _create_vector_store(self, store_type: str, store_path: str):
        """创建向量存储"""
        if store_type == "auto":
            # 自动选择可用的向量存储
            available_stores = list_available_stores()
            config = get_store_config("auto")
            
            for preferred_type in config["priority"]:
                if preferred_type in available_stores:
                    store_type = preferred_type
                    break
            else:
                raise RuntimeError("没有可用的向量存储类型")
        
        # 创建具体的向量存储实例
        if store_type == "memory":
            return MemoryVectorStore(self.embeddings)
        elif store_type.startswith("faiss_"):
            store_config = get_store_config(store_type)
            index_type = store_config.get("index_type", "IndexFlatL2")
            vector_store = FAISSVectorStore(self.embeddings, index_type, store_path)
            # 尝试加载现有存储
            vector_store.load()
            return vector_store
        else:
            raise ValueError(f"不支持的向量存储类型: {store_type}")
    
    def _get_current_store_name(self) -> str:
        """获取当前存储类型的显示名称"""
        info = self.vector_store.get_info()
        return info.get("type", "unknown")
    
    def process_document(self, file_path: str, file_content: bytes = None) -> tuple[bool, str]:
        """处理文档并添加到向量存储，返回(成功状态, 文档ID)"""
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                return False, None
            
            filename = Path(file_path).name
            
            # 加载文档
            file_extension = Path(file_path).suffix.lower() #后缀
            
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
                documents = loader.load()   # 加载（每页一个 Document）
            elif file_extension == '.txt':
                # 直接读取文本文件内容，支持多种编码
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='gbk') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, 'r', encoding='latin1') as f:
                            content = f.read()
                
                # 创建Document对象
                from langchain.schema import Document
                documents = [Document(page_content=content, metadata={"source": file_path})]
            else:
                return False, None

            # 分割文档
            chunks = self.text_splitter.split_documents(documents)
            
            # 为每个chunk添加document_id到metadata
            doc_id = str(self.next_doc_id)
            for chunk in chunks:
                chunk.metadata["document_id"] = doc_id
                chunk.metadata["filename"] = filename
            
            # 添加到向量存储
            success = self.vector_store.add_documents(chunks)
            
            if success:
                # 记录文档信息
                self.document_metadata[doc_id] = {
                    "filename": filename,
                    "chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "file_path": file_path,
                    "deleted": False  # 软删除标记位
                }
                self.next_doc_id += 1
                
                if hasattr(self.vector_store, 'save'):
                    save_result = self.vector_store.save()

                
                # 保存document metadata
                self._save_document_metadata()
                
                return True, doc_id
            else:
                print(f"❌ 向量存储添加失败")
            
            return False, None
            
        except Exception as e:
            print(f"❌ 处理文档时出现异常: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def rag_chat(self, query: str, use_context: bool = True) -> str:
        """RAG聊天"""
        if not use_context:
            return self.chat_model.generate_response(query)
        
        try:
            # 检索相关文档 - 过滤已删除的文档
            search_k = min(9, 20)  # 搜索更多结果以应对删除过滤
            results = self.vector_store.similarity_search_with_score(query, k=search_k) #过滤已删除的文档
            filtered_results = self._filter_deleted_documents(results)
            filtered_results = filtered_results[:3]  # 限制最终结果为3个
            
            if not filtered_results:
                return self.chat_model.generate_response(query, "注意：没有找到相关文档，请基于常识回答。")
            
            # 构建上下文
            context_parts = []
            for doc, score in filtered_results:
                context_parts.append(f"文档内容：{doc.page_content}")
            
            context = "\n\n".join(context_parts)
            
            return self.chat_model.generate_response(query, context)
            
        except Exception as e:
            return self.chat_model.generate_response(query)
    
    def rag_chat_stream(self, query: str, use_context: bool = True) -> Generator[str, None, None]:
        """RAG流式聊天"""
        if not use_context:
            yield from self.chat_model.generate_stream_response(query)
            return
        
        try:
            # 检索相关文档 - 过滤已删除的文档
            search_k = min(9, 20)  # 搜索更多结果以应对删除过滤
            results = self.vector_store.similarity_search_with_score(query, k=search_k)
            filtered_results = self._filter_deleted_documents(results)
            filtered_results = filtered_results[:3]  # 限制最终结果为3个
            
            if not filtered_results:
                yield from self.chat_model.generate_stream_response(query, "注意：没有找到相关文档，请基于常识回答。")
            else:
                # 构建上下文
                context_parts = []
                for doc, score in filtered_results:
                    context_parts.append(f"文档内容：{doc.page_content}")
                
                context = "\n\n".join(context_parts)
                yield from self.chat_model.generate_stream_response(query, context)
            
        except Exception as e:
            yield from self.chat_model.generate_stream_response(query)
    
    def get_status(self) -> dict:
        """获取RAG服务状态"""
        store_info = self.vector_store.get_info()
        
        # 添加文档计数信息
        store_info["documents"] = len(self.document_metadata)
        store_info["document_list"] = list(self.document_metadata.keys())
        
        return {
            "available": True,
            "vector_store": store_info,
            "embedding_model": config.ollama_embedding_model,
            "chat_model": config.ollama_model
        }
    
    def _filter_deleted_documents(self, search_results):
        """过滤已删除的文档"""
        filtered_results = []
        for doc, score in search_results:
            # 直接从metadata中获取document_id
            document_id = doc.metadata.get('document_id')
            
            # 如果文档有document_id且被标记为删除，则跳过
            if document_id and self.document_metadata.get(document_id, {}).get('deleted', False):
                continue  # 跳过已删除的文档
                
            filtered_results.append((doc, score))
        
        return filtered_results

    def search_documents(self, query: str, k: int = 3) -> list:
        """搜索相关文档 - 自动过滤已删除的文档"""
        try:
            # 获取更多结果以应对删除过滤
            search_k = min(k * 3, 20)  # 搜索更多结果，但限制在合理范围内
            results = self.vector_store.similarity_search_with_score(query, k=search_k)
            
            # 过滤已删除的文档
            filtered_results = self._filter_deleted_documents(results)
            
            # 限制返回结果数量
            filtered_results = filtered_results[:k]
            
            documents = []
            for doc, score in filtered_results:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            return documents
        except Exception as e:
            return []
    
    def delete_document(self, document_id: str) -> dict:
        """软删除文档 - 通过标记位实现"""
        try:
            # 检查文档是否存在
            if document_id not in self.document_metadata:
                available_ids = list(self.document_metadata.keys())
                return {
                    "success": False,
                    "message": f"文档ID {document_id} 不存在",
                    "error": f"当前可用的文档ID: {available_ids}。总共有 {len(available_ids)} 个文档。"
                }
            
            doc_info = self.document_metadata[document_id]
            
            # 检查是否已经被删除
            if doc_info.get("deleted", False):
                return {
                    "success": False,
                    "message": f"文档 '{doc_info['filename']}' 已经被删除",
                    "error": "此文档已被标记为删除状态"
                }
            
            # 软删除：标记为删除状态
            self.document_metadata[document_id]["deleted"] = True
            self.document_metadata[document_id]["deleted_timestamp"] = datetime.now().isoformat()
            
            # 保存更新的metadata
            self._save_document_metadata()
            
            return {
                "success": True,
                "message": f"文档 '{doc_info['filename']}' 已成功删除",
                "detail": "文档已被标记为删除，不会在搜索中出现"
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "删除文档时发生错误",
                "error": f"技术详情: {str(e)}"
            }
    
    def list_documents(self, include_deleted: bool = False) -> list:
        """列出文档（默认不包含已删除的文档）"""
        try:
            documents = []
            for doc_id, doc_info in self.document_metadata.items():
                # 如果不包含已删除文档，则跳过已删除的
                if not include_deleted and doc_info.get("deleted", False):
                    continue
                    
                documents.append({
                    "id": doc_id,
                    "name": doc_info["filename"],
                    "chunks": doc_info["chunks"],
                    "timestamp": doc_info["timestamp"],
                    "file_path": doc_info.get("file_path", ""),
                    "deleted": doc_info.get("deleted", False)
                })
            return documents
        except Exception as e:
            return []
    
    def clear_store(self) -> dict:
        """清空向量存储"""
        try:
            # 重新创建空的向量存储
            self._create_vector_store(self.store_type, self.store_path)
            return {
                "success": True,
                "message": "向量存储已清空"
            }
        except Exception as e:
            return {
                "success": False,
                "message": "清空存储时出错",
                "error": str(e)
            }