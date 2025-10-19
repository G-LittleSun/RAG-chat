#!/usr/bin/env python3
"""
ChromaDB 数据库查看工具
用于查看和检查 ChromaDB 向量数据库中的内容
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chromadb
from core.config import config


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    else:
        print("-" * 70)


def view_chromadb():
    """查看 ChromaDB 数据库内容"""
    
    try:
        # 连接到 ChromaDB
        store_path = config.get_vector_db_path()
        print(f"📂 连接到 ChromaDB: {store_path}")
        
        client = chromadb.PersistentClient(path=store_path)
        
        # 列出所有集合
        print_separator("所有集合")
        collections = client.list_collections()
        
        if not collections:
            print("❌ 没有找到任何集合")
            return
        
        print(f"找到 {len(collections)} 个集合:")
        for col in collections:
            print(f"  • {col.name}")
        
        # 获取默认集合
        collection_name = config.chromadb_collection_name
        print_separator(f"集合详情: {collection_name}")
        
        try:
            collection = client.get_collection(name=collection_name)
        except Exception as e:
            print(f"❌ 无法获取集合 '{collection_name}': {e}")
            print("\n可用的集合:")
            for col in collections:
                print(f"  • {col.name}")
            return
        
        # 显示集合统计
        doc_count = collection.count()
        print(f"📊 文档总数: {doc_count}")
        
        if doc_count == 0:
            print("❌ 集合为空，没有文档")
            return
        
        # 获取所有数据
        print_separator("文档概览")
        all_data = collection.get()
        
        print(f"文档ID数量: {len(all_data['ids'])}")
        print(f"文档内容数量: {len(all_data['documents'])}")
        print(f"元数据数量: {len(all_data['metadatas'])}")
        
        # 显示前几个文档ID
        print("\n📝 前10个文档ID:")
        for i, doc_id in enumerate(all_data['ids'][:10], 1):
            print(f"  {i}. {doc_id}")
        
        # 统计文件名
        print_separator("文件统计")
        filenames = {}
        for metadata in all_data['metadatas']:
            if metadata and 'filename' in metadata:
                filename = metadata['filename']
                filenames[filename] = filenames.get(filename, 0) + 1
        
        if filenames:
            print(f"共 {len(filenames)} 个不同的文件:")
            for filename, count in sorted(filenames.items()):
                print(f"  • {filename}: {count} 个文档块")
        else:
            print("⚠️  没有找到文件名元数据")
        
        # 显示文档示例
        print_separator("文档内容示例")
        
        for i in range(min(3, len(all_data['documents']))):
            print(f"\n📄 文档 #{i+1}:")
            print(f"ID: {all_data['ids'][i]}")
            
            if all_data['metadatas'][i]:
                print(f"元数据: {all_data['metadatas'][i]}")
            
            content = all_data['documents'][i]
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"内容预览: {preview}")
            print("-" * 70)
        
        # 交互式查询
        print_separator("交互式功能")
        print("\n💡 提示:")
        print("  1. 查看特定文件: collection.get(where={'filename': '文件名.pdf'})")
        print("  2. 搜索内容: collection.query(query_texts=['问题'], n_results=5)")
        print("  3. 删除集合: client.delete_collection(name='集合名')")
        print("  4. 清空集合: collection.delete(ids=all_data['ids'])")
        
    except ImportError:
        print("❌ ChromaDB 未安装，请运行: pip install chromadb")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def search_chromadb(query: str, n_results: int = 5):
    """搜索 ChromaDB"""
    try:
        store_path = config.get_vector_db_path()
        client = chromadb.PersistentClient(path=store_path)
        collection = client.get_collection(name=config.chromadb_collection_name)
        
        print(f"🔍 搜索: {query}")
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        print(f"\n找到 {len(results['ids'][0])} 个相关文档:")
        for i, (doc_id, doc, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\n{i}. ID: {doc_id}")
            print(f"   距离: {distance:.4f}")
            print(f"   元数据: {metadata}")
            print(f"   内容: {doc[:150]}...")
            
    except Exception as e:
        print(f"❌ 搜索失败: {e}")


def main():
    """主函数"""
    print("=" * 70)
    print("  ChromaDB 数据库查看工具")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        # 命令行参数：搜索模式
        query = " ".join(sys.argv[1:])
        search_chromadb(query)
    else:
        # 默认：查看所有内容
        view_chromadb()
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()