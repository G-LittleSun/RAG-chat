"""
配置管理模块
管理应用的各种配置参数
"""
import os
from typing import Optional
from dataclasses import dataclass

# 装饰器，简化存储数据的类的定义。
# 自动生成方法：__init__、__repr__、__eq__
# 类型注解支持：强制使用类型提示
# 默认值设置：支持字段默认值
# 灵活配置：通过参数控制行为

@dataclass
class Config:
    """应用配置类"""
    
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:1.5b"
    ollama_embedding_model: str = "nomic-embed-text"  # 嵌入模型
    
    # FastAPI配置
    host: str = "0.0.0.0"  # 允许外部访问
    port: int = 8000
    debug: bool = True   # 开发环境下详细错误信息、修改代码后自动重载页面
    
    # HTTPS/SSL配置
    enable_https: bool = True   # 启用HTTPS以提供更安全的文档问答
    ssl_cert_path: str = "ssl/server.crt"  # SSL证书路径
    ssl_key_path: str = "ssl/server.key"   # SSL私钥路径
    ssl_port: int = 8443  # HTTPS端口
    
    # 聊天配置
    select_history_length: int = 10  # 聊天历史长度
    max_history_length: int = 50  # 最大聊天历史长度
    streaming: bool = True  # 是否启用流式响应
    
    # 数据库配置
    database_url: Optional[str] = None  # 为后续SQL数据库扩展预留
    vector_db_path: str = "data/vector_store"  # 向量数据库路径
    document_metadata_path: str = "data/document_metadata.json"  # 文档元数据路径
    upload_path: str = "data/uploads"  # 文档上传路径
    
    # 向量存储配置
    # 可选值: "auto", "chromadb", "faiss_ip", "faiss_l2", "faiss_hnsw", "memory"
    # auto: 自动选择可用的向量存储（按优先级：faiss_ip > chromadb > faiss_l2 > faiss_hnsw > memory）
    vector_store_type: str = "auto"  # 向量存储类型
    chromadb_collection_name: str = "rag_documents"  # ChromaDB集合名称
    
    # ChromaDB 远程服务器配置（可选）
    # 如果设置了 chromadb_remote_host，将使用远程服务器而不是本地存储
    chromadb_remote_host: Optional[str] = None  # 远程服务器地址，例如: "192.168.1.100" 或 "chromadb.example.com"
    chromadb_remote_port: int = 8000  # 远程服务器端口
    chromadb_use_ssl: bool = False  # 是否使用 HTTPS 连接远程服务器
    chromadb_api_token: Optional[str] = None  # API 认证令牌（如果远程服务器需要）
    
    # 系统提示词
    system_prompt: str = (
        "You are a helpful AI assistant. You can help with coding, "
        "answering questions, and general conversation. Please be "
        "concise and helpful in your responses."
    )
    
    def get_vector_db_path(self) -> str:
        """获取向量数据库的绝对路径"""
        if os.path.isabs(self.vector_db_path):
            return self.vector_db_path
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.vector_db_path)
    
    def get_document_metadata_path(self) -> str:
        """获取文档元数据文件的绝对路径"""
        if os.path.isabs(self.document_metadata_path):
            return self.document_metadata_path
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.document_metadata_path)
    
    def get_upload_path(self) -> str:
        """获取上传目录的绝对路径"""
        if os.path.isabs(self.upload_path):
            return self.upload_path
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.upload_path)

    def get_ssl_cert_path(self) -> str:
        """获取SSL证书的绝对路径"""
        if os.path.isabs(self.ssl_cert_path):
            return self.ssl_cert_path
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.ssl_cert_path)
    
    def get_ssl_key_path(self) -> str:
        """获取SSL私钥的绝对路径"""
        if os.path.isabs(self.ssl_key_path):
            return self.ssl_key_path
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.ssl_key_path)
    
    def ssl_files_exist(self) -> bool:
        """检查SSL证书文件是否存在"""
        cert_path = os.path.join(os.path.dirname(__file__), self.ssl_cert_path)
        key_path = os.path.join(os.path.dirname(__file__), self.ssl_key_path)
        return os.path.exists(cert_path) and os.path.exists(key_path)


# 全局配置实例
config = Config()