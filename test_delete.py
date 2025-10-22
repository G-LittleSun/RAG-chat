#!/usr/bin/env python3
"""
测试硬删除和软删除功能
"""

from core.simple_rag_service import SimpleRAGService
from pathlib import Path

def test_delete_functions():
    """测试删除功能"""
    
    print("\n" + "="*60)
    print("🧪 测试文档删除功能")
    print("="*60)
    
    # 初始化RAG服务（使用ChromaDB）
    print("\n1️⃣ 初始化RAG服务（ChromaDB）...")
    rag = SimpleRAGService(vector_store_type="chromadb")
    
    # 查看当前文档列表
    print("\n2️⃣ 当前文档列表:")
    docs = rag.list_documents()
    for doc in docs:
        status = "❌ 已删除" if doc.get('deleted') else "✅ 活跃"
        print(f"  - ID: {doc['id']}, 名称: {doc['name']}, 状态: {status}, 块数: {doc['chunks']}")
    
    if not docs:
        print("  ⚠️ 没有文档，请先上传一些文档进行测试")
        return
    
    # 选择第一个文档进行测试
    test_doc_id = docs[0]['id']
    test_doc_name = docs[0]['name']
    
    print(f"\n3️⃣ 测试文档: ID={test_doc_id}, 名称={test_doc_name}")
    
    # 测试硬删除
    print(f"\n4️⃣ 执行硬删除...")
    result = rag.delete_document(test_doc_id)
    
    print(f"\n删除结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 消息: {result['message']}")
    if 'detail' in result:
        print(f"  - 详情: {result['detail']}")
    if 'error' in result:
        print(f"  - 错误: {result['error']}")
    
    # 再次查看文档列表
    print("\n5️⃣ 删除后的文档列表:")
    docs_after = rag.list_documents()
    for doc in docs_after:
        status = "❌ 已删除" if doc.get('deleted') else "✅ 活跃"
        print(f"  - ID: {doc['id']}, 名称: {doc['name']}, 状态: {status}, 块数: {doc['chunks']}")
    
    # 检查删除的文档是否还在
    deleted_doc_found = any(doc['id'] == test_doc_id for doc in docs_after)
    
    if deleted_doc_found:
        print(f"\n⚠️ 警告: 文档 {test_doc_id} 仍在列表中（可能是软删除）")
    else:
        print(f"\n✅ 成功: 文档 {test_doc_id} 已完全从系统中移除（硬删除）")
    
    # 查看向量存储信息
    print("\n6️⃣ 向量存储信息:")
    status = rag.get_status()
    vector_info = status.get('vector_store', {})
    print(f"  - 类型: {vector_info.get('type', 'unknown')}")
    print(f"  - 文档数: {vector_info.get('documents', 0)}")
    print(f"  - 总块数: {vector_info.get('chunks', 0)}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)

if __name__ == "__main__":
    test_delete_functions()
