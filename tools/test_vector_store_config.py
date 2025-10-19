#!/usr/bin/env python3
"""
向量存储切换测试脚本
用于验证不同向量数据库的配置和切换功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vector_stores.vector_config import list_available_stores, get_store_config, VECTOR_STORES


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print("-" * 60)


def test_list_available_stores():
    """测试可用的向量存储列表"""
    print_separator("测试: 列出可用的向量存储")
    
    available = list_available_stores()
    print(f"✅ 找到 {len(available)} 个可用的向量存储:")
    for store in available:
        config = VECTOR_STORES.get(store, {})
        print(f"  - {store}: {config.get('name', 'Unknown')}")
    
    return available


def test_store_configs():
    """测试向量存储配置"""
    print_separator("测试: 向量存储配置详情")
    
    for store_type, config in VECTOR_STORES.items():
        print(f"\n📦 {store_type}:")
        print(f"   名称: {config.get('name')}")
        print(f"   模块: {config.get('module')}")
        print(f"   类名: {config.get('class')}")
        print(f"   持久化: {'✅' if config.get('persistent') else '❌'}")
        
        if 'index_type' in config:
            print(f"   索引类型: {config.get('index_type')}")
        if 'collection_name' in config:
            print(f"   集合名称: {config.get('collection_name')}")


def test_auto_config():
    """测试自动配置"""
    print_separator("测试: 自动配置选择")
    
    config = get_store_config("auto")
    print(f"配置类型: {config.get('type')}")
    print(f"优先级顺序: {config.get('priority')}")
    
    available = list_available_stores()
    print(f"\n根据优先级，将选择: ", end="")
    for store_type in config.get('priority', []):
        if store_type in available:
            store_name = VECTOR_STORES.get(store_type, {}).get('name', store_type)
            print(f"✅ {store_type} ({store_name})")
            break
    else:
        print("❌ 没有可用的向量存储")


def test_import_stores():
    """测试导入各个向量存储类"""
    print_separator("测试: 导入向量存储类")
    
    # 测试 MemoryVectorStore
    try:
        from vector_stores.memory_vector_store import MemoryVectorStore
        print("✅ MemoryVectorStore 导入成功")
    except ImportError as e:
        print(f"❌ MemoryVectorStore 导入失败: {e}")
    
    # 测试 FAISSVectorStore
    try:
        from vector_stores.faiss_vector_store import FAISSVectorStore
        print("✅ FAISSVectorStore 导入成功")
    except ImportError as e:
        print(f"❌ FAISSVectorStore 导入失败: {e}")
    
    # 测试 ChromaDBVectorStore
    try:
        from vector_stores.chromadb_vector_store import ChromaDBVectorStore
        print("✅ ChromaDBVectorStore 导入成功")
    except ImportError as e:
        print(f"❌ ChromaDBVectorStore 导入失败: {e}")


def test_dependencies():
    """测试依赖库"""
    print_separator("测试: 依赖库检查")
    
    # 检查 FAISS
    try:
        import faiss
        print("✅ FAISS 已安装")
        print(f"   版本: {faiss.__version__ if hasattr(faiss, '__version__') else 'Unknown'}")
    except ImportError:
        print("❌ FAISS 未安装")
        print("   安装命令: pip install faiss-cpu")
    
    # 检查 ChromaDB
    try:
        import chromadb
        print("✅ ChromaDB 已安装")
        print(f"   版本: {chromadb.__version__ if hasattr(chromadb, '__version__') else 'Unknown'}")
    except ImportError:
        print("❌ ChromaDB 未安装")
        print("   安装命令: pip install chromadb")
    
    # 检查 LangChain
    try:
        from langchain_community.vectorstores import DocArrayInMemorySearch
        print("✅ DocArrayInMemorySearch 已安装")
    except ImportError:
        print("❌ DocArrayInMemorySearch 未安装")
    
    try:
        from langchain_community.vectorstores import FAISS
        print("✅ LangChain FAISS 支持已安装")
    except ImportError:
        print("❌ LangChain FAISS 支持未安装")
    
    try:
        from langchain_community.vectorstores import Chroma
        print("✅ LangChain Chroma 支持已安装")
    except ImportError:
        print("❌ LangChain Chroma 支持未安装")


def test_config_file():
    """测试配置文件"""
    print_separator("测试: 配置文件读取")
    
    try:
        from core.config import config
        print(f"✅ 配置文件加载成功")
        print(f"   向量存储类型: {config.vector_store_type}")
        print(f"   向量存储路径: {config.vector_db_path}")
        print(f"   ChromaDB集合名: {config.chromadb_collection_name}")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")


def main():
    """主测试函数"""
    print("="*60)
    print("  向量存储配置测试工具")
    print("="*60)
    
    # 运行所有测试
    test_dependencies()
    test_import_stores()
    test_list_available_stores()
    test_store_configs()
    test_auto_config()
    test_config_file()
    
    print_separator()
    print("\n✅ 测试完成!")
    print("\n💡 使用提示:")
    print("   1. 在 core/config.py 中修改 vector_store_type 配置")
    print("   2. 可选值: 'auto', 'chromadb', 'faiss_ip', 'faiss_l2', 'faiss_hnsw', 'memory'")
    print("   3. 使用 'auto' 会自动选择最优的可用向量存储")
    print("   4. 查看 docs/VECTOR_STORE_CONFIGURATION.md 了解更多详情")
    print()


if __name__ == "__main__":
    main()
