"""
核心模块包
包含应用的核心组件
"""

# 导入核心组件，提供统一的API接口
try:
    from .config import config   #.config相对导入，导入当前包的config模块。..为上级包,...为上上级包
    __all__ = ['config']
    print("OK core.config 加载成功")
except ImportError as e:
    print(f"WARNING config 导入失败: {e}")
    __all__ = []

try:
    from .models import ChatModel
    __all__.append('ChatModel')
    print("OK core.models 加载成功")
except ImportError as e:
    print(f"WARNING models 导入失败: {e}")

try:
    from .simple_rag_service import SimpleRAGService
    __all__.append('SimpleRAGService')
    print("OK core.simple_rag_service 加载成功")
except ImportError as e:
    print(f"WARNING simple_rag_service 导入失败: {e}")

try:
    from .session_manager import SessionManager
    __all__.append('SessionManager')
    print("OK core.session_manager 加载成功")
except ImportError as e:
    print(f"WARNING session_manager 导入失败: {e}")

# 包信息
__version__ = "1.0.0"
__author__ = "RAG System"