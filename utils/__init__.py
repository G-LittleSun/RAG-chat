"""
工具模块包
包含各种辅助工具和集成
"""

# 导入核心工具类，提供便捷的导入接口
try:
    from .ssl_manager import SSLCertificateManager
    __all__ = ['SSLCertificateManager']
    print("OK utils.ssl_manager 加载成功")
except ImportError as e:
    print(f"WARNING ssl_manager 导入失败: {e}")
    __all__ = []

# 注意：faiss_integration 依赖其他模块，暂时不导入
# 可以通过 from utils.faiss_integration import xxx 来使用

# 包信息
__version__ = "1.0.0"
__author__ = "RAG System"