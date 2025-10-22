# 文档删除功能说明

## 概述

系统现在提供了两种删除方式：**软删除** 和 **硬删除**。

## 删除方式对比

### 1. 软删除 (`soft_delete_document`)

**适用场景**：
- 使用不支持删除操作的向量数据库（如 FAISS）
- 需要保留文档历史记录
- 可能需要恢复删除的文档

**工作原理**：
- 文档仍保留在向量存储中
- 在 `document_metadata` 中标记 `deleted: True`
- 搜索时通过过滤器自动排除已删除的文档

**优点**：
- 兼容所有向量数据库
- 可以轻松恢复
- 保留完整历史

**缺点**：
- 占用存储空间
- 搜索性能略有影响（需要过滤）

### 2. 硬删除 (`delete_document`)

**适用场景**：
- 使用支持删除操作的向量数据库（如 ChromaDB）
- 需要释放存储空间
- 确定不需要恢复的文档

**工作原理**：
- 从向量存储中完全删除所有文档块
- 从 `document_metadata` 中移除文档记录
- 如果向量存储不支持删除，自动降级为软删除

**优点**：
- 完全释放存储空间
- 提高搜索性能
- 数据更干净

**缺点**：
- 无法恢复
- 仅支持特定向量数据库

## 实现细节

### ChromaDB 硬删除实现

在 `chromadb_vector_store.py` 中新增 `delete_by_metadata` 方法：

```python
def delete_by_metadata(self, metadata_filter: dict) -> dict:
    """
    根据metadata过滤条件删除文档
    
    Args:
        metadata_filter: 元数据过滤条件，例如 {"document_id": "123"}
        
    Returns:
        dict: 包含成功状态、删除数量等信息
    """
```

**工作流程**：
1. 获取集合中的所有文档
2. 根据 metadata 过滤条件匹配文档
3. 收集需要删除的文档 ID
4. 调用 `collection.delete(ids=ids_to_delete)` 删除

### RAG 服务删除方法

#### `soft_delete_document(document_id: str) -> dict`

```python
# 软删除示例
result = rag_service.soft_delete_document("123")
# 结果：文档被标记为已删除，但仍在向量存储中
```

#### `delete_document(document_id: str) -> dict`

```python
# 硬删除示例
result = rag_service.delete_document("123")
# 结果：
# - 如果是 ChromaDB：从向量存储中完全删除
# - 如果是 FAISS：自动降级为软删除
```

## 向量数据库支持情况

| 向量数据库 | 硬删除支持 | 自动降级 |
|-----------|----------|---------|
| ChromaDB  | ✅ 支持  | N/A     |
| FAISS     | ❌ 不支持 | ✅ 自动软删除 |
| Memory    | ❌ 不支持 | ✅ 自动软删除 |

## 使用建议

### 何时使用软删除？

1. **使用 FAISS 向量数据库**
2. **不确定是否需要恢复**
3. **需要保留审计记录**
4. **临时隐藏文档**

### 何时使用硬删除？

1. **使用 ChromaDB 向量数据库**
2. **确定不再需要该文档**
3. **需要释放存储空间**
4. **清理测试数据**

## 测试

运行测试脚本：

```bash
python test_delete.py
```

测试内容：
- 初始化 RAG 服务
- 列出当前文档
- 执行硬删除
- 验证删除结果
- 检查向量存储状态

## 返回值格式

### 成功示例

```json
{
    "success": true,
    "message": "文档 'example.pdf' 已成功删除",
    "detail": "已从向量存储中删除 15 个文档块，并清除所有记录"
}
```

### 失败示例

```json
{
    "success": false,
    "message": "文档ID 999 不存在",
    "error": "当前可用的文档ID: ['0', '1', '2']。总共有 3 个文档。"
}
```

## 注意事项

1. **硬删除不可逆**：一旦执行硬删除，无法恢复
2. **自动降级**：如果向量存储不支持删除，会自动使用软删除
3. **metadata 保存**：删除操作会自动保存 metadata 文件
4. **向量存储保存**：如果向量存储支持 save 方法，会自动保存

## 迁移说明

### 从旧版本升级

旧版本的 `delete_document` 已重命名为 `soft_delete_document`。

如果你的代码中使用了：
```python
rag_service.delete_document(doc_id)
```

现在有两个选择：

1. **继续使用软删除**：
   ```python
   rag_service.soft_delete_document(doc_id)
   ```

2. **改用硬删除**（推荐，如果使用 ChromaDB）：
   ```python
   rag_service.delete_document(doc_id)  # 自动判断是否支持硬删除
   ```

## 未来改进

- [ ] 批量删除功能
- [ ] 软删除恢复功能
- [ ] 删除历史记录
- [ ] 定时清理软删除文档
- [ ] 更多向量数据库的硬删除支持
