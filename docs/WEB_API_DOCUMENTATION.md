# 🌐 Web API接口详细文档

## 📋 API接口概览

### 🏠 页面路由

#### `GET /`
**描述**: 重定向到聊天界面主页  
**返回**: 重定向响应到 `/chat`

#### `GET /chat`
**描述**: 返回聊天界面HTML页面  
**返回**: HTML页面 (`static/chat.html`)

#### `GET /ws-test`
**描述**: WebSocket测试页面  
**返回**: HTML页面 (`static/ws-test.html`)

---

### 💬 聊天相关API

#### `POST /api/chat`
**描述**: 发送聊天消息，获取AI回复

**请求体**:
```json
{
    "message": "你好，世界！",
    "session_id": "optional-session-id",
    "system_prompt": "optional-system-prompt"
}
```

**响应**:
```json
{
    "response": "AI生成的回复内容",
    "session_id": "session-uuid"
}
```

**状态码**:
- `200`: 成功
- `500`: 模型服务不可用

#### `GET /api/sessions`
**描述**: 获取所有活跃会话列表

**响应**:
```json
{
    "sessions": ["session-id-1", "session-id-2"]
}
```

#### `GET /api/sessions/{session_id}/history`
**描述**: 获取指定会话的聊天历史

**路径参数**:
- `session_id`: 会话ID

**响应**:
```json
{
    "history": [
        {
            "role": "user",
            "content": "用户消息",
            "timestamp": "2023-01-01T12:00:00"
        },
        {
            "role": "assistant", 
            "content": "AI回复",
            "timestamp": "2023-01-01T12:00:01"
        }
    ]
}
```

**状态码**:
- `200`: 成功
- `404`: 会话不存在

#### `DELETE /api/sessions/{session_id}`
**描述**: 删除指定会话

**路径参数**:
- `session_id`: 会话ID

**响应**:
```json
{
    "success": true,
    "message": "会话删除成功"
}
```

**状态码**:
- `200`: 删除成功
- `404`: 会话不存在

---

### 📚 RAG文档问答API

#### `GET /api/rag/status`
**描述**: 获取RAG服务状态和可用性信息

**响应**:
```json
{
    "available": true,
    "store_info": {
        "type": "FAISS-IndexFlatIP",
        "documents": 3,
        "available": true,
        "persistent": true,
        "document_list": ["0", "1", "2"]
    }
}
```

#### `POST /api/documents/upload`
**描述**: 上传文档到向量存储

**请求**: `multipart/form-data`
- `file`: 文档文件 (PDF/Word/TXT)

**响应**:
```json
{
    "success": true,
    "message": "文档上传成功",
    "document_id": "123",
    "filename": "document.pdf",
    "chunks": 5
}
```

**状态码**:
- `200`: 上传成功
- `400`: 文件格式不支持
- `500`: 处理失败
- `501`: RAG功能不可用

#### `GET /api/documents`
**描述**: 获取所有文档列表

**响应**:
```json
{
    "documents": [
        {
            "id": "0",
            "name": "document1.pdf",
            "chunks": 5,
            "timestamp": "2023-01-01T12:00:00",
            "file_path": "data/uploads/document1.pdf",
            "deleted": false
        }
    ],
    "vector_store": {
        "type": "FAISS-IndexFlatIP",
        "documents": 1,
        "available": true,
        "persistent": true,
        "document_list": ["0"]
    }
}
```

#### `DELETE /api/documents/{document_id}`
**描述**: 删除指定文档（软删除）

**路径参数**:
- `document_id`: 文档ID

**响应**:
```json
{
    "success": true,
    "message": "文档删除成功",
    "document_id": "123"
}
```

**状态码**:
- `200`: 删除成功
- `404`: 文档不存在
- `409`: 文档已被删除
- `501`: RAG功能不可用

#### `POST /api/documents/chat`
**描述**: 基于文档内容进行问答

**请求体**:
```json
{
    "message": "文档中提到了什么？",
    "session_id": "optional-session-id"
}
```

**响应**:
```json
{
    "response": "根据文档内容生成的回答",
    "session_id": "session-uuid",
    "sources": [
        {
            "content": "相关文档片段",
            "metadata": {
                "document_id": "123",
                "source": "document.pdf"
            }
        }
    ]
}
```

#### `POST /api/documents/chat/stream`
**描述**: 基于文档的流式问答

**请求体**: 同上

**响应**: `text/plain` 流式响应
```
data: 根据
data: 文档
data: 内容...
```

#### `GET /api/documents/store/info`
**描述**: 获取向量存储详细信息

**响应**:
```json
{
    "type": "FAISS-IndexFlatIP",
    "documents": 3,
    "available": true,
    "persistent": true,
    "document_list": ["0", "1", "2"],
    "index_size": 1500,
    "dimension": 384
}
```

#### `DELETE /api/documents/store/clear`
**描述**: 清空所有文档和向量存储

**响应**:
```json
{
    "success": true,
    "message": "文档存储已清空",
    "deleted_documents": 3
}
```

#### `POST /api/documents/search`
**描述**: 搜索文档内容

**请求体**:
```json
{
    "query": "搜索关键词",
    "k": 5
}
```

**响应**:
```json
{
    "results": [
        {
            "content": "匹配的文档内容片段",
            "score": 0.95,
            "metadata": {
                "document_id": "123",
                "source": "document.pdf",
                "chunk_index": 0
            }
        }
    ],
    "total": 1
}
```

---

### 🔌 WebSocket接口

#### `WebSocket /ws/{session_id}`
**描述**: 实时聊天WebSocket连接

**路径参数**:
- `session_id`: 会话ID

**消息格式**:

**发送消息**:
```json
{
    "type": "chat",
    "message": "用户消息内容",
    "use_rag": false
}
```

**接收消息**:
```json
{
    "type": "response",
    "content": "AI回复内容"
}
```

**流式消息**:
```json
{
    "type": "stream",
    "content": "部分回复内容"
}
```

**错误消息**:
```json
{
    "type": "error",
    "message": "错误描述"
}
```

**连接状态**:
```json
{
    "type": "connected",
    "session_id": "session-uuid"
}
```

---

### 🏥 系统监控API

#### `GET /health`
**描述**: 服务健康检查

**响应**:
```json
{
    "status": "healthy",
    "timestamp": "2023-01-01T12:00:00",
    "services": {
        "ollama": "available",
        "rag": "available",
        "vector_store": "available"
    },
    "version": "3.0.0"
}
```

---

## 📝 数据模型

### 聊天请求模型
```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    system_prompt: Optional[str] = None
```

### 聊天响应模型
```python
class ChatResponse(BaseModel):
    response: str
    session_id: str
```

### 文档上传响应模型
```python
class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: str
    filename: str
    chunks: int
```

### 搜索请求模型
```python
class SearchRequest(BaseModel):
    query: str
    k: int = 5
```

---

## 🔧 错误处理

### HTTP状态码说明

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `409 Conflict`: 资源冲突（如文档已删除）
- `500 Internal Server Error`: 服务器内部错误
- `501 Not Implemented`: 功能未实现或不可用

### 错误响应格式
```json
{
    "detail": "错误详细描述",
    "error_code": "ERROR_CODE",
    "timestamp": "2023-01-01T12:00:00"
}
```

---

## 📚 使用示例

### Python客户端示例

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 普通聊天
def chat_example():
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "你好，世界！"
    })
    result = response.json()
    print(f"AI回复: {result['response']}")
    return result['session_id']

# 上传文档
def upload_document():
    with open("document.pdf", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    result = response.json()
    print(f"文档ID: {result['document_id']}")
    return result['document_id']

# 文档问答
def rag_chat_example():
    response = requests.post(f"{BASE_URL}/api/documents/chat", json={
        "message": "文档中的主要内容是什么？"
    })
    result = response.json()
    print(f"回答: {result['response']}")
    if 'sources' in result:
        print(f"参考来源: {len(result['sources'])} 个片段")

# WebSocket聊天示例
import asyncio
import websockets

async def websocket_chat():
    uri = "ws://localhost:8000/ws/test-session"
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send(json.dumps({
            "type": "chat",
            "message": "你好！",
            "use_rag": False
        }))
        
        # 接收回复
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if data["type"] == "response":
                print(f"完整回复: {data['content']}")
                break
            elif data["type"] == "stream":
                print(data["content"], end="", flush=True)

# 运行示例
if __name__ == "__main__":
    # 普通聊天
    session_id = chat_example()
    
    # 上传并问答
    doc_id = upload_document()
    rag_chat_example()
    
    # WebSocket聊天
    asyncio.run(websocket_chat())
```

### JavaScript/前端示例

```javascript
// 普通聊天API调用
async function chatWithAI(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    });
    const result = await response.json();
    return result.response;
}

// 文档上传
async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    return result.document_id;
}

// WebSocket连接
function connectWebSocket(sessionId) {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'response') {
            console.log('AI回复:', data.content);
        } else if (data.type === 'stream') {
            // 处理流式内容
            process.stdout.write(data.content);
        }
    };
    
    // 发送消息
    ws.send(JSON.stringify({
        type: 'chat',
        message: '你好！',
        use_rag: false
    }));
}
```

---

## 🚀 性能和限制

### 请求限制
- 单次文档上传: 最大 50MB
- 文档问答上下文: 最多检索 5 个相关片段
- WebSocket连接: 每个session_id只允许一个连接
- 聊天历史: 每个会话最多保存 50 条消息

### 支持的文档格式
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- 纯文本 (.txt)

### 向量存储性能
- FAISS IndexFlatIP: 适合中小规模数据 (< 100万向量)
- 向量维度: 384 (nomic-embed-text)
- 批量处理: 支持批量文档上传和处理

---

**API版本**: v3.0.0  
**最后更新**: 2025年9月23日