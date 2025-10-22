"""
FastAPI Web服务
提供REST API和WebSocket接口，包含文档问答功能
"""
import uuid
import json
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from core.config import config
from core.session_manager import session_manager

# 导入 Gradio 界面
try:
    import gradio as gr
    from gradio_ui import create_gradio_app
    GRADIO_ENABLED = True
except ImportError:
    GRADIO_ENABLED = False
    print("⚠️  Gradio 界面不可用 - 请安装 gradio: pip install gradio")

# 导入模块化的RAG服务
try:
    from core.simple_rag_service import SimpleRAGService as DocumentRAGService
    from core.config import config
    RAG_ENABLED = True
    
    # 使用配置文件中的路径，auto自动选择最优的向量存储
    _rag_service = DocumentRAGService(vector_store_type="auto", store_path=config.get_vector_db_path())
    
    def get_rag_service():
        """获取RAG服务实例"""
        return _rag_service
    
    def process_uploaded_file(file_path: str):
        """处理上传的文件"""
        success, document_id = _rag_service.process_document(file_path)
        
        if success:
            # 获取存储状态信息
            status = _rag_service.get_status()
            vector_store_info = status.get("vector_store", {})
            
            return {
                "success": True,
                "message": "文档上传成功",
                "document_id": document_id,
                "chunks_created": 1,  # 简化版本不跟踪具体块数
                "total_docs_in_store": vector_store_info.get("documents", 0)
            }
        else:
            return {
                "success": False,
                "message": "文档处理失败",
                "error": "无法处理文档"
            }
    
    def chat_with_documents(message: str, history=None):
        """与文档聊天"""
        # 目前简单实现，不使用history，直接调用RAG
        response = _rag_service.rag_chat(message)
        return {"response": response}
    
    def chat_with_documents_stream(message: str, history=None):
        """流式与文档聊天"""
        return _rag_service.rag_chat_stream(message)
    
    def delete_document(document_id: str):
        """删除文档"""
        if _rag_service is None:
            return {
                "success": False,
                "message": "删除失败",
                "error": "RAG服务未初始化"
            }
        return _rag_service.delete_document(document_id)
    
    def is_rag_available():
        """检查RAG是否可用"""
        return _rag_service is not None
        
except ImportError:
    RAG_ENABLED = False
    print("⚠️  RAG功能不可用 - 相关依赖未安装")


# 请求/响应模型
class ChatRequest(BaseModel):
    message: str
    session_id: str = None
    use_documents: bool = False  # 是否使用文档问答模式


class RAGChatRequest(BaseModel):
    message: str
    session_id: str = None
    max_context_docs: int = 3


class ChatResponse(BaseModel):
    response: str
    session_id: str
    has_context: bool = False
    sources: List[Dict[str, Any]] = []


class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: str = None
    error: str = None
    file_info: Dict[str, Any] = None


class SessionInfo(BaseModel):
    session_id: str
    message_count: int


class StoreInfo(BaseModel):
    status: str
    document_count: int
    is_ready: bool


# 创建FastAPI应用
app = FastAPI(
    title="Ollama Chat API",
    description="基于Ollama和LangChain的聊天API服务",
    version="1.0.0"
)

# 添加CORS中间件，允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 挂载 Gradio 界面到 /gradio 路径
if GRADIO_ENABLED and RAG_ENABLED:
    try:
        # 导入 ChatModel
        from core.models import ChatModel
        
        # 创建 ChatModel 实例（用于普通聊天）
        chat_model = ChatModel()
        
        # 创建 Gradio 应用
        gradio_app = create_gradio_app(
            chat_model=chat_model,
            session_manager=session_manager,
            rag_service=_rag_service
        )
        
        # 挂载到 FastAPI
        app = gr.mount_gradio_app(app, gradio_app, path="/gradio")
        print("✅ Gradio 界面已挂载到 /gradio")
    except Exception as e:
        print(f"⚠️  Gradio 挂载失败: {str(e)}")
elif not GRADIO_ENABLED:
    print("⚠️  Gradio 未启用 - 请安装 gradio: pip install gradio")
elif not RAG_ENABLED:
    print("⚠️  RAG 服务未启用 - Gradio 界面需要 RAG 支持")



class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)


manager = ConnectionManager()


@app.get("/manifest.json")
async def get_manifest():
    """返回 PWA manifest 文件"""
    from fastapi.responses import FileResponse
    manifest_path = Path("static/manifest.json")
    if manifest_path.exists():
        return FileResponse(manifest_path, media_type="application/json")
    else:
        # 如果文件不存在，返回一个基本的 manifest
        return {
            "name": "RAG Chat System",
            "short_name": "RAG Chat",
            "start_url": "/",
            "display": "standalone"
        }


@app.get("/")
async def read_root():
    """根路径，返回简单的HTML页面"""
    gradio_link = '<p>🎨 Gradio 界面: <a href="/gradio">/gradio</a> (推荐)</p>' if GRADIO_ENABLED else ''
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ollama Chat</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
            }}
            .links {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .links p {{
                margin: 10px 0;
                font-size: 16px;
            }}
            a {{
                color: #0066cc;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .recommended {{
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #2196f3;
            }}
        </style>
    </head>
    <body>
        <h1>🤖 RAG-Chat 智能对话系统</h1>
        <div class="links">
            <h2>访问入口</h2>
            {gradio_link}
            <p>📖 API文档: <a href="/docs">/docs</a></p>
            <p>💬 聊天界面(旧版): <a href="/chat">/chat</a></p>
            <p>📚 RAG聊天界面(旧版): <a href="/rag-chat">/rag-chat</a></p>
            <p>🧪 WebSocket测试: <a href="/ws-test">/ws-test</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/chat")
async def chat_page():
    """聊天页面"""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static", "chat.html")
    with open(static_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/ws-test")
async def ws_test_page():
    """WebSocket测试页面"""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static", "ws-test.html")
    with open(static_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """普通聊天API端点"""
    try:
        # 生成会话ID（如果没有提供）
        session_id = request.session_id or str(uuid.uuid4())
        
        # 获取会话
        session = session_manager.get_session(session_id)
        
        # 生成响应
        response = session.chat(request.message)
        
        return ChatResponse(response=response, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """获取所有会话列表"""
    sessions = []
    for session_id in session_manager.list_sessions():
        session = session_manager.get_session(session_id)
        sessions.append(SessionInfo(
            session_id=session_id,
            message_count=len(session.get_history())
        ))
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """获取指定会话的历史记录"""
    if session_id not in session_manager.list_sessions():
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_manager.get_session(session_id)
    return {"history": session.get_history()}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除指定会话"""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 断开WebSocket连接
    manager.disconnect(session_id)
    
    return {"message": "Session deleted successfully"}


# ==================== 文档问答API ====================

@app.get("/api/rag/status")
async def rag_status():
    """获取RAG功能状态"""
    if not RAG_ENABLED:
        return {
            "available": False,
            "error": "FAISS dependencies not installed",
            "install_command": "pip install faiss-cpu python-multipart pypdf python-docx unstructured"
        }
    
    rag_service = get_rag_service()
    if rag_service is None:
        return {
            "available": False,
            "error": "RAG service initialization failed"
        }
    
    store_info = rag_service.get_status()
    return {
        "available": True,
        "store_info": store_info
    }


@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传文档并处理"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    # 检查文件类型
    allowed_extensions = {'.pdf', '.txt', '.docx', '.doc'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型: {file_extension}. 支持的类型: {list(allowed_extensions)}"
        )
    
    # 检查文件大小（限制为10MB）
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    
    try:
        # 使用配置文件中的上传目录
        uploads_dir = Path(config.get_upload_path())
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一的文件名
        import uuid
        unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        save_path = uploads_dir / unique_filename
        
        # 保存文件到配置的上传目录
        content = await file.read()
        with open(save_path, 'wb') as f:
            f.write(content)
        
        # 处理文档
        result = process_uploaded_file(str(save_path))
        
        # 注意：这里不删除文件，保留在data目录中供后续使用
        
        if result["success"]:
            return DocumentUploadResponse(
                success=True,
                message=result["message"],
                document_id=result.get("document_id"),
                file_info={
                    "filename": file.filename,
                    "size": len(content),
                    "type": file_extension,
                    "chunks_created": result.get("chunks_created", 0),
                    "total_docs_in_store": result.get("total_docs_in_store", 0)
                }
            )
        else:
            return DocumentUploadResponse(
                success=False,
                message="文档处理失败",
                error=result.get("error", "未知错误")
            )
            
    except Exception as e:
        # 如果出错，删除已保存的文件（如果存在）
        if 'save_path' in locals() and os.path.exists(save_path):
            os.unlink(save_path)
        
        raise HTTPException(status_code=500, detail=f"处理文档时出错: {str(e)}")


@app.post("/api/documents/chat", response_model=ChatResponse)
async def chat_with_documents_endpoint(request: RAGChatRequest):
    """基于文档的问答"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    try:
        # 生成会话ID（如果没有提供）
        session_id = request.session_id or str(uuid.uuid4())
        
        # 获取会话历史
        session = session_manager.get_session(session_id)
        history = session.get_history()
        
        # 使用RAG进行对话
        result = chat_with_documents(request.message, history)
        
        # 将对话添加到会话历史
        session.add_message("user", request.message)
        session.add_message("assistant", result["response"])
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            has_context=result.get("has_context", False),
            sources=result.get("sources", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/chat/stream")
async def chat_with_documents_stream_endpoint(request: RAGChatRequest):
    """基于文档的流式问答"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    try:
        # 生成会话ID（如果没有提供）
        session_id = request.session_id or str(uuid.uuid4())
        
        # 获取会话历史
        session = session_manager.get_session(session_id)
        history = session.get_history()
        
        # 流式生成器
        def generate_stream():
            full_response = ""
            for chunk in chat_with_documents_stream(request.message, history):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # 将对话添加到会话历史
            session.add_message("user", request.message)
            session.add_message("assistant", full_response)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/store/info")
async def get_store_info():
    """获取向量存储信息"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    rag_service = get_rag_service()
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG服务不可用")
    
    info = rag_service.get_status()
    vector_store_info = info.get("vector_store", {})
    
    # 构造符合StoreInfo模型的数据
    store_info_data = {
        "status": "ready" if info.get("available", False) else "not_ready",
        "document_count": vector_store_info.get("documents", 0),
        "is_ready": info.get("available", False)
    }
    
    return StoreInfo(**store_info_data)


@app.get("/api/documents")
async def get_documents_list():
    """获取文档列表"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(status_code=503, detail="RAG服务不可用")
        
        # 获取文档列表
        documents = rag_service.list_documents()
        status = rag_service.get_status()
        
        return {
            "documents": documents,
            "vector_store": status.get("vector_store", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表时出错: {str(e)}")


@app.delete("/api/documents/{document_id}")
async def delete_document_by_id(document_id: str):
    """删除指定文档"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    try:
        result = delete_document(document_id)  # 直接传递字符串
        
        # 确保result是字典类型
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="删除操作返回格式错误")
        
        if result.get("success", False):
            return {"message": result.get("message", "删除成功")}
        else:
            error_msg = result.get("error", result.get("message", "删除失败"))
            
            # 检查错误类型
            if "不存在" in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            elif "已经被删除" in error_msg or "已被标记为删除" in error_msg:
                raise HTTPException(status_code=409, detail=error_msg)  # Conflict
            else:
                # 其他错误（如真正不支持的操作）
                raise HTTPException(status_code=501, detail=error_msg)
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 捕获所有其他异常
        raise HTTPException(status_code=500, detail=f"删除文档时出错: {str(e)}")


@app.delete("/api/documents/store/clear")
async def clear_document_store():
    """清空文档存储"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    rag_service = get_rag_service()
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG服务不可用")
    
    result = rag_service.clear_store()
    if result["success"]:
        return {"message": result["message"]}
    else:
        raise HTTPException(status_code=500, detail=result["error"])


@app.post("/api/documents/search")
async def search_documents(request: dict):
    """搜索相关文档"""
    if not RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG功能不可用")
    
    query = request.get("query", "")
    k = request.get("k", 5)
    
    if not query:
        raise HTTPException(status_code=400, detail="查询内容不能为空")
    
    rag_service = get_rag_service()
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG服务不可用")
    
    results = rag_service.search_documents(query, k=k)
    return {"documents": results, "query": query, "count": len(results)}


# ==================== 增强的WebSocket端点 ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket聊天端点，支持流式响应和文档问答"""
    await manager.connect(websocket, session_id)
    session = session_manager.get_session(session_id)
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            print(f"🔍 收到WebSocket消息: {data}")  # 调试信息
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            use_documents = message_data.get("use_documents", False)
            
            print(f"📝 用户消息: {user_message}")  # 调试信息
            print(f"🔖 使用文档模式: {use_documents}")  # 调试信息
            print(f"🔄 RAG功能可用: {RAG_ENABLED}")  # 调试信息
            
            if not user_message:
                continue
            
            # 发送确认消息
            await manager.send_message(json.dumps({
                "type": "user_message",
                "content": user_message,
                "use_documents": use_documents
            }), session_id)
            
            # 开始流式响应
            await manager.send_message(json.dumps({
                "type": "assistant_start"
            }), session_id)
            
            # 根据模式选择响应方式
            full_response = ""
            sources = []
            
            if use_documents and RAG_ENABLED:
                # 使用文档问答模式
                print("📚 启动文档问答模式...")  # 调试信息
                history = session.get_history()
                try:
                    for chunk in chat_with_documents_stream(user_message, history):
                        full_response += chunk
                        await manager.send_message(json.dumps({
                            "type": "assistant_chunk",
                            "content": chunk
                        }), session_id)
                    
                    print(f"✅ 文档问答完成，响应长度: {len(full_response)}")  # 调试信息
                except Exception as e:
                    print(f"❌ 文档问答错误: {str(e)}")  # 调试信息
                    error_msg = f"文档问答时出错: {str(e)}"
                    full_response = error_msg
                    await manager.send_message(json.dumps({
                        "type": "assistant_chunk",
                        "content": error_msg
                    }), session_id)
                
                # 获取相关文档信息
                try:
                    rag_service = get_rag_service()
                    if rag_service:
                        docs = rag_service.search_documents(user_message, k=3)
                        sources = [{"preview": doc["content"][:100] + "...", 
                                   "relevance": doc["relevance"]} for doc in docs]
                        print(f"📄 找到相关文档: {len(sources)}个")  # 调试信息
                except Exception as e:
                    print(f"⚠️ 获取文档信息错误: {str(e)}")  # 调试信息
            else:
                # 使用普通聊天模式
                print("💬 启动普通聊天模式...")  # 调试信息
                try:
                    chunk_count = 0
                    for chunk in session.chat_stream(user_message):
                        chunk_count += 1
                        full_response += chunk
                        await manager.send_message(json.dumps({
                            "type": "assistant_chunk",
                            "content": chunk
                        }), session_id)
                    
                    print(f"✅ 普通聊天完成，总块数: {chunk_count}，响应长度: {len(full_response)}")  # 调试信息
                except Exception as e:
                    print(f"❌ 普通聊天错误: {str(e)}")  # 调试信息
                    error_msg = f"普通聊天时出错: {str(e)}"
                    full_response = error_msg
                    await manager.send_message(json.dumps({
                        "type": "assistant_chunk",
                        "content": error_msg
                    }), session_id)
            
            # 发送响应结束标志
            await manager.send_message(json.dumps({
                "type": "assistant_end",
                "full_content": full_response,
                "sources": sources,
                "has_context": bool(sources)
            }), session_id)
    
    except WebSocketDisconnect:
        print(f"🔌 WebSocket连接断开: {session_id}")  # 调试信息
        manager.disconnect(session_id)
    except Exception as e:
        print(f"❌ WebSocket处理错误: {str(e)}")  # 调试信息
        print(f"💡 错误类型: {type(e).__name__}")  # 调试信息
        # 发送错误消息
        try:
            await manager.send_message(json.dumps({
                "type": "error",
                "content": f"发生错误: {str(e)}"
            }), session_id)
        except:
            print("⚠️ 无法发送错误消息到WebSocket")  # 调试信息
        manager.disconnect(session_id)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "session_count": session_manager.get_session_count(),
        "model": config.ollama_model,
        "rag_available": RAG_ENABLED
    }


if __name__ == "__main__":
    # 打印启动信息
    print("🚀 启动Ollama Chat服务...")
    print(f"📖 Ollama模型: {config.ollama_model}")
    print(f"🌐 Ollama地址: {config.ollama_base_url}")
    
    if RAG_ENABLED:
        print("🔍 RAG功能: ✅ 可用")
    else:
        print("🔍 RAG功能: ❌ 不可用（需要安装: pip install faiss-cpu python-multipart pypdf python-docx unstructured）")
    
    print("=" * 50)
    
    # 配置SSL并启动服务器
    import uvicorn
    ssl_keyfile = None
    ssl_certfile = None
    use_https = False
    server_port = config.port
    
    # 方式1：检查 config.enable_https（主配置）
    if getattr(config, 'enable_https', False):
        try:
            from utils.ssl_manager import SSLCertificateManager
            ssl_manager = SSLCertificateManager('ssl')
            
            # 确保证书存在且有效
            if not ssl_manager.certificate_exists() or not ssl_manager.certificate_valid():
                print("🔐 正在生成SSL证书...")
                success = ssl_manager.generate_certificate()
                if not success:
                    raise Exception("SSL证书生成失败")
            
            ssl_keyfile = ssl_manager.key_path
            ssl_certfile = ssl_manager.cert_path
            use_https = True
            print("🔒 HTTPS已启用 (通过SSL管理器)")
            
        except Exception as e:
            print(f"⚠️  SSL配置失败: {e}")
            use_https = False
    
    # 方式2：检查 config.use_ssl（备用配置）
    elif getattr(config, 'use_ssl', False):
        if hasattr(config, 'ssl_files_exist') and config.ssl_files_exist():
            import os
            ssl_keyfile = os.path.join(os.path.dirname(__file__), config.ssl_key_path)
            ssl_certfile = os.path.join(os.path.dirname(__file__), config.ssl_cert_path)
            server_port = getattr(config, 'ssl_port', config.port)
            use_https = True
            print("🔒 HTTPS已启用 (直接证书文件)")
        else:
            print("⚠️  警告：SSL已启用但证书文件不存在，回退到HTTP模式")
            print("   请运行 generate_ssl.bat 生成证书")
    
    if not use_https:
        print(f"🔓 HTTP模式: 启用 (端口 {server_port})")
    else:
        print(f"🔒 HTTPS模式: 启用 (端口 {server_port})")
    
    print(f"📋 API文档: {'https' if use_https else 'http'}://localhost:{server_port}/docs")
    print(f"💬 聊天界面: {'https' if use_https else 'http'}://localhost:{server_port}/chat")
    
    # 启动服务器
    uvicorn.run(
        "app:app",
        host=config.host,
        port=server_port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        reload=config.debug,
        access_log=False
    )


def run_server_with_ssl():
    """强制启用SSL启动服务器 - 提供给外部调用的辅助函数"""
    import os
    import uvicorn
    
    # 检查SSL证书文件
    cert_path = os.path.join(os.path.dirname(__file__), config.ssl_cert_path)
    key_path = os.path.join(os.path.dirname(__file__), config.ssl_key_path)
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("❌ SSL证书文件不存在！")
        print("请先运行以下命令生成证书：")
        print("  Windows: generate_ssl.bat")
        print("  Linux/Mac: ./generate_ssl.sh")
        return False
    
    print("🔒 启动HTTPS服务器...")
    uvicorn.run(
        "app:app",
        host=config.host,
        port=getattr(config, 'ssl_port', config.port),
        reload=config.debug,
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )
    return True
    """启动服务器 - 统一的启动逻辑，支持多种SSL配置方式"""
    import os
    import uvicorn
    
    ssl_keyfile = None
    ssl_certfile = None
    use_https = False
    server_port = config.port
    
    # 方式1：检查 config.enable_https（主配置）
    if getattr(config, 'enable_https', False):
        try:
            from utils.ssl_manager import SSLCertificateManager
            ssl_manager = SSLCertificateManager('ssl')
            
            # 确保证书存在且有效
            if not ssl_manager.certificate_exists() or not ssl_manager.certificate_valid():
                print("� 正在生成SSL证书...")
                success = ssl_manager.generate_certificate()
                if not success:
                    raise Exception("SSL证书生成失败")
            
            ssl_keyfile = ssl_manager.key_path
            ssl_certfile = ssl_manager.cert_path
            use_https = True
            print("🔒 HTTPS已启用 (通过SSL管理器)")
            
        except Exception as e:
            print(f"⚠️  SSL配置失败: {e}")
            use_https = False
    
    # 方式2：检查 config.use_ssl（备用配置）
    elif getattr(config, 'use_ssl', False):
        if hasattr(config, 'ssl_files_exist') and config.ssl_files_exist():
            ssl_keyfile = os.path.join(os.path.dirname(__file__), config.ssl_key_path)
            ssl_certfile = os.path.join(os.path.dirname(__file__), config.ssl_cert_path)
            server_port = getattr(config, 'ssl_port', config.port)
            use_https = True
            print("🔒 HTTPS已启用 (直接证书文件)")
        else:
            print("⚠️  警告：SSL已启用但证书文件不存在，回退到HTTP模式")
            print("   请运行 generate_ssl.bat 生成证书")
    
    if not use_https:
        print(f"🔓 HTTP模式: 启用 (端口 {server_port})")
    else:
        print(f"🔒 HTTPS模式: 启用 (端口 {server_port})")
    
    print(f"📋 API文档: {'https' if use_https else 'http'}://localhost:{server_port}/docs")
    print(f"💬 聊天界面: {'https' if use_https else 'http'}://localhost:{server_port}/chat")
    
    # 启动服务器
    uvicorn.run(
        "app:app",
        host=config.host,
        port=server_port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        reload=config.debug,
        access_log=False
    )

